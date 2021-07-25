//+------------------------------------------------------------------+
//|                                     CyrusChartToolsConnector.mq4 |
//|                        Copyright 2021, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, Cyrus Engine"
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict


// Required: MQL-ZMQ from https://github.com/dingmaotu/mql-zmq

#include <Zmq/Zmq.mqh>

extern string PROJECT_NAME = "CyrusChartToolsConnector";
extern string ZEROMQ_PROTOCOL = "tcp";
extern string HOSTNAME = "*";
extern int PUSH_PORT = 32771;
extern int PULL_PORT = 32772;
extern int PUB_PORT = 32773;
extern int MILLISECOND_TIMER = 1;



// Dynamic array initialized at OnInit(). Can be updated by TRACK_PRICES requests from client peers
string Publish_Symbols[];
string Publish_Symbols_LastTick[];

// CREATE ZeroMQ Context
Context context(PROJECT_NAME);

// CREATE ZMQ_PUSH SOCKET
Socket pushSocket(context, ZMQ_PUSH);

// CREATE ZMQ_PULL SOCKET
Socket pullSocket(context, ZMQ_PULL);

// CREATE ZMQ_PUB SOCKET
Socket pubSocket(context, ZMQ_PUB);

// VARIABLES FOR LATER
uchar _data[];
ZmqMsg request;




//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {

   EventSetMillisecondTimer(MILLISECOND_TIMER);     // Set Millisecond Timer to get client socket input

   context.setBlocky(false);

   // Send responses to PULL_PORT that client is listening on.
   if(!pushSocket.bind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PULL_PORT))) {
      Print("[PUSH] ####ERROR#### Binding MT4 Server to Socket on Port " + IntegerToString(PULL_PORT) + "..");
      return(INIT_FAILED);
   } else {
      Print("[PUSH] Binding MT4 Server to Socket on Port " + IntegerToString(PULL_PORT) + "..");
      pushSocket.setSendHighWaterMark(1);
      pushSocket.setLinger(0);
   }

   // Receive commands from PUSH_PORT that client is sending to.
   if(!pullSocket.bind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PUSH_PORT))) {
      Print("[PULL] ####ERROR#### Binding MT4 Server to Socket on Port " + IntegerToString(PUSH_PORT) + "..");
      return(INIT_FAILED);
   } else {
      Print("[PULL] Binding MT4 Server to Socket on Port " + IntegerToString(PUSH_PORT) + "..");
      pullSocket.setReceiveHighWaterMark(1);
      pullSocket.setLinger(0);
   }

   // Send new market data to PUB_PORT that client is subscribed to.
   if(!pubSocket.bind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PUB_PORT))) {
      Print("[PUB] ####ERROR#### Binding MT4 Server to Socket on Port " + IntegerToString(PUB_PORT) + "..");
      return(INIT_FAILED);
   } else {
      Print("[PUB] Binding MT4 Server to Socket on Port " + IntegerToString(PUB_PORT) + "..");
      pubSocket.setSendHighWaterMark(1);
      pubSocket.setLinger(0);
   }
   return(INIT_SUCCEEDED);
}
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {

   Print("[PUSH] Unbinding MT4 Server from Socket on Port " + IntegerToString(PULL_PORT) + "..");
   pushSocket.unbind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PULL_PORT));
   pushSocket.disconnect(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PULL_PORT));

   Print("[PULL] Unbinding MT4 Server from Socket on Port " + IntegerToString(PUSH_PORT) + "..");
   pullSocket.unbind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PUSH_PORT));
   pullSocket.disconnect(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PUSH_PORT));

   if (Publish_MarketData == true || Publish_MarketRates == true) {
      Print("[PUB] Unbinding MT4 Server from Socket on Port " + IntegerToString(PUB_PORT) + "..");
      pubSocket.unbind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PUB_PORT));
      pubSocket.disconnect(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PUB_PORT));
   }

   // Shutdown ZeroMQ Context
   context.shutdown();
   context.destroy(0);

   EventKillTimer();
}
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---
   
  }
//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer() {

   /*
      Use this OnTimer() function to get and respond to commands
   */

   if(CheckServerStatus() == true) {
      // Get client's response, but don't block.
      pullSocket.recv(request, true);

      if (request.size() > 0) {
         // Wait
         // pullSocket.recv(request,false);

         // MessageHandler() should go here.
         ZmqMsg reply = MessageHandler(request);

         // Send response, and block
         // pushSocket.send(reply);

         // Send response, but don't block
         if(!pushSocket.send(reply, true)) {
           Print("###ERROR### Sending message");
         }
      }

      // update prices regularly in case there was no tick within X milliseconds (for non-chart symbols).
      if (GetTickCount() >= lastUpdateMillis + MILLISECOND_TIMER_PRICES) OnTick();
   }
}
//+------------------------------------------------------------------+

ZmqMsg MessageHandler(ZmqMsg &_request) {

   // Output object
   ZmqMsg reply;

   // Message components for later.
   string components[11];

   if(_request.size() > 0) {

      // Get data from request
      ArrayResize(_data, _request.size());
      _request.getData(_data);
      string dataStr = CharArrayToString(_data);

      // Process data
      ParseZmqMessage(dataStr, components);

      // Interpret data
      InterpretZmqMessage(pushSocket, components);

   } else {
      // NO DATA RECEIVED
   }

   return(reply);
}


//+------------------------------------------------------------------+
// Interpret Zmq Message and perform actions
void InterpretZmqMessage(Socket &pSocket, string &compArray[]) {

   // Message Structures:

   // 1) Get Symbols

   // 2) Get Data

   //  HIST|SYMBOL|TIMEFRAME|START_DATETIME|END_DATETIME

   // 3) Draw

   // NOTE: datetime has format: D'2015.01.01 00:00'

   /*
      compArray[0] = Get_Symbols, HIST, Draw

      If Draw ->
         compArray[0] = DRAW
         compArray[1] = TYPE (e.g. VLine, HLine, TrendLine, ...)

         // Object TYPES:
         // https://docs.mql4.com/constants/objectconstants/enum_object

         compArray[2] = Chart Id
         compArray[3] = Name
         compArray[4] = Sub Window
         compArray[5] = Color
         ...
         
   // 4) Clear
   */

   int switch_action = 0;

   /* 02-08-2019 10:41 CEST - HEARTBEAT */
   if(compArray[0] == "HEARTBEAT")
      InformPullClient(pSocket, "{'_action': 'heartbeat', '_response': 'loud and clear!'}");

   /* Process Messages */
   if(compArray[0] == "GET_SYMBOLS")
      switch_action = 1;
   if(compArray[0] == "HIST")
      switch_action = 2;
   if(compArray[0] == "DRAW")
      switch_action = 3;
   if(compArray[0] == "CLEAR")
      switch_action = 4;


   // IMPORTANT: when adding new functions, also increase the max switch_action in CheckOpsStatus()!

   /* Setup processing variables */
   string zmq_ret = "";
   string ret = "";
   int ticket = -1;
   bool ans = false;

   /****************************
    * PERFORM SOME CHECKS HERE *
    ****************************/
   if (CheckOpsStatus(pSocket, switch_action) == true) {

      switch(switch_action) {
         case 1: // GET_SYMBOL

            zmq_ret = "{";

            // Function definition:
            GetSymbols(zmq_ret);

            // Send TICKET back as JSON
            InformPullClient(pSocket, zmq_ret + "}");

            break;


         case 2: // HIST

            zmq_ret = "{";

            GetHist(compArray, zmq_ret);

            InformPullClient(pSocket, zmq_ret + "}");

            break;

         case 3: // DRAW

            zmq_ret = "{";

            // IMPLEMENT CLOSE TRADE LOGIC HERE
            Draw(compArray, zmq_ret);

            InformPullClient(pSocket, zmq_ret + "}");

            break;
            
         case 4: // Clear
            
            zmq_ret = "{";

            // IMPLEMENT CLOSE TRADE LOGIC HERE
            Clear(zmq_ret);

            InformPullClient(pSocket, zmq_ret + "}");

         default:
            break;
      }
   }
}

// Check if operations are permitted
bool CheckOpsStatus(Socket &pSocket, int switch_action) {

   if (switch_action >= 1 && switch_action <= 10) {

      if (!IsTradeAllowed()) {
         InformPullClient(pSocket, "{'_response': 'TRADING_IS_NOT_ALLOWED__ABORTED_COMMAND'}");
         return(false);
      }
      else if (!IsExpertEnabled()) {
         InformPullClient(pSocket, "{'_response': 'EA_IS_DISABLED__ABORTED_COMMAND'}");
         return(false);
      }
      else if (IsTradeContextBusy()) {
         InformPullClient(pSocket, "{'_response': 'TRADE_CONTEXT_BUSY__ABORTED_COMMAND'}");
         return(false);
      }
      else if (!IsDllsAllowed()) {
         InformPullClient(pSocket, "{'_response': 'DLLS_DISABLED__ABORTED_COMMAND'}");
         return(false);
      }
      else if (!IsLibrariesAllowed()) {
         InformPullClient(pSocket, "{'_response': 'LIBS_DISABLED__ABORTED_COMMAND'}");
         return(false);
      }
      else if (!IsConnected()) {
         InformPullClient(pSocket, "{'_response': 'NO_BROKER_CONNECTION__ABORTED_COMMAND'}");
         return(false);
      }
   }

   return(true);
}

// Parse Zmq Message
void ParseZmqMessage(string& message, string& retArray[]) {

   //Print("Parsing: " + message);

   string sep = ";";
   ushort u_sep = StringGetCharacter(sep,0);

   int splits = StringSplit(message, u_sep, retArray);

   /*
   for(int i = 0; i < splits; i++) {
      Print(IntegerToString(i) + ") " + retArray[i]);
   }
   */
}


void GetSymbols(string& compArray[], string& zmq_ret){
   
   // Foramt: GET_SYMBOLS
   long currChart,prevChart=ChartFirst();
   int i=0,limit=100;
   Print("ChartFirst =",ChartSymbol(prevChart)," ID =",prevChart);
   zmq_ret = zmq_ret + "'_action': 'GET_SYMBOLS', '_symbols': [{'Symbol': '" + ChartSymbol(prevChart) + "', 'ID': '" + prevChart + "'}";
   while(i<limit)// We have certainly not more than 100 open charts
     {
      currChart=ChartNext(prevChart); // Get the new chart ID by using the previous chart ID
      if(currChart<0) break;          // Have reached the end of the chart list
      prevChart=currChart;// let's save the current chart ID for the ChartNext()
      i++;// Do not forget to increase the counter
      zmq_ret = zmq_ret + ", {'Symbol': '" + ChartSymbol(prevChart) + "', 'ID': '" + prevChart + "'}";
      VLineCreate(currChart, "VLine"+time, 0, Time[time], 0xFFFFFF);
     }
     zmq_ret = zmq_ret + "]";
   
}


//+------------------------------------------------------------------+
// Get historic for request datetime range
void GetHist(string& compArray[], string& zmq_ret) {

   // Format: HIST|SYMBOL|TIMEFRAME|COUNT

   string _symbol = compArray[1];
   ENUM_TIMEFRAMES _timeframe = (ENUM_TIMEFRAMES)StrToInteger(compArray[2]);

   MqlRates rates_array[];

   // Get prices
   int rates_count = 0;

   // Handling ERR_HISTORY_WILL_UPDATED (4066) and ERR_NO_HISTORY_DATA (4073) errors.
   // For non-chart symbols and time frames MT4 often needs a few requests until the data is available.
   // But even after 10 requests it can happen that it is not available. So it is best to have the charts open.
   for (int i=0; i<10; i++) {
      rates_count = CopyRates(_symbol, _timeframe, 0, compArray[3], rates_array);
      int errorCode = GetLastError();
      // Print("errorCode: ", errorCode);
      if (rates_count > 0 || (errorCode != 4066 && errorCode != 4073)) break;
      Sleep(200);
   }

   zmq_ret = zmq_ret + "'_action': 'HIST', '_symbol': '" + _symbol+ "_" + GetTimeframeText(_timeframe) + "'";

   // if data then forms response as json:
   // {'_action: 'HIST',
   //  '_data':[{'time': 'YYYY:MM:DD,HH:MM:SS', 'Open':0.0, 'High':0.0, 'Low':0.0, 'Close':0.0, 'Volume':0},
   //           {...},
   //           ...
   //          ]
   // }
   if (rates_count > 0) {

      zmq_ret = zmq_ret + ", '_data': [";

      // Construct string of rates and send to PULL client.
      for(int i = 0; i < rates_count; i++ ) {

         if(i == 0)
            zmq_ret = zmq_ret + "{'Time':'" + TimeToString(rates_array[i].time) + "', 'Open':" + DoubleToString(rates_array[i].open) +
             ", 'High':" + DoubleToString(rates_array[i].high) + ", 'Low':" + DoubleToString(rates_array[i].low) + ", 'Close':" +
              DoubleToString(rates_array[i].close) + ", 'Volume':" + IntegerToString(rates_array[i].tick_volume) + "}";
         else
            zmq_ret = zmq_ret + ", {'Time':'" + TimeToString(rates_array[i].time) + "', 'Open':" + DoubleToString(rates_array[i].open) +
             ", 'High':" + DoubleToString(rates_array[i].high) + ", 'Low':" + DoubleToString(rates_array[i].low) + ", 'Close':" +
              DoubleToString(rates_array[i].close) + ", 'Volume':" + IntegerToString(rates_array[i].tick_volume) + "}";

      }

      zmq_ret = zmq_ret + "]";

   }
   // if NO data then forms response as json:
   // {'_action: 'HIST',
   //  '_response': 'NOT_AVAILABLE'
   // }
   else {
      zmq_ret = zmq_ret + ", " + "'_response': 'NOT_AVAILABLE'";
   }
}


void Clear(string zmq_ret&){
   
}


void Draw(string& compArray[], string zmq_ret&){

   /* 
      compArray[1] : Type
      
      Types:
      VLine, HLine, TREND, ...
   */
   
   zmq_ret = zmq_ret + "'_action': 'DRAW'"
   
   if compArray[1] == "VLINE":
      swithAction = 1;
   if(compArray[1] == "HLINE")
      switch_action = 1;
   if(compArray[1] == "TREND")
      switch_action = 2;
      
   switch(switch_action) {
         case 1: // GET_SYMBOL
            // Foramt : ChartId | Name | SubWindow | Time | Color | Style | Width | Back | Selection | Hidden | ZOrder
            // Function definition:
            bool success = VLineCreate(StringToInteger(compArray[2], compArray[3], StrToInteger(compArray[4]), StrToTime(compArray[5]), StringToColor(compArray[6]), StrToInteger(compArray[7]), StrToInteger(compArray[8]),
            StrToInteger(compArray[9]), StrToInteger(compArray[10]), StrToInteger(compArray[11]), StrToInteger(compArray[12]), zmq_ret)
            
            if (success)
               zmq_ret = zmq_ret + ", '_result': 'Successed' }";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed' }";
            break;


         case 2: // HIST

            zmq_ret = "{";

            GetHist(compArray, zmq_ret);

            InformPullClient(pSocket, zmq_ret + "}");

            break;

         case 3: // DRAW

            zmq_ret = "{";

            // IMPLEMENT CLOSE TRADE LOGIC HERE
            DRAW(compArray, zmq_ret);

            InformPullClient(pSocket, zmq_ret + "}");

            break;

         default:
            break;
      }
   
}


bool VLineCreate(const long            chart_ID=0,        // chart's ID
                 const string          name="VLine",      // line name
                 const int             sub_window=0,      // subwindow index
                 datetime              time=0,            // line time
                 const color           clr=clrRed,        // line color
                 const ENUM_LINE_STYLE style=STYLE_SOLID, // line style
                 const int             width=1,           // line width
                 const bool            back=false,        // in the background
                 const bool            selection=true,    // highlight to move
                 const bool            hidden=true,       // hidden in the object list
                 const long            z_order=0)         // priority for mouse click
  {
//--- if the line time is not set, draw it via the last bar
   if(!time)
      time=TimeCurrent();
//--- reset the error value
   ResetLastError();
//--- create a vertical line
   if(!ObjectCreate(chart_ID,name,OBJ_VLINE,sub_window,time,0))
     {
      Print(__FUNCTION__,
            ": failed to create a vertical line! Error code = ",GetLastError());
      return(false);
     }
//--- set line color
   ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
//--- set line display style
   ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
//--- set line width
   ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
//--- display in the foreground (false) or background (true)
   ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
//--- enable (true) or disable (false) the mode of moving the line by mouse
//--- when creating a graphical object using ObjectCreate function, the object cannot be
//--- highlighted and moved by default. Inside this method, selection parameter
//--- is true by default making it possible to highlight and move the object
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTED,selection);
//--- hide (true) or display (false) graphical object name in the object list
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
//--- set the priority for receiving the event of a mouse click in the chart
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
//--- successful execution
   return(true);
  }
