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
extern int MILLISECOND_TIMER_PRICES = 500;

//extern string t1 = "--- ZeroMQ Configuration ---";
bool Publish_MarketData  = false;
bool Publish_MarketRates = false;

long lastUpdateMillis = GetTickCount();

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


/**
 * Class definition for an specific instrument: the tuple (symbol,timeframe)
 */
class Instrument {
public:

    //--------------------------------------------------------------
    /** Instrument constructor */
    Instrument() { _symbol = ""; _name = ""; _timeframe = PERIOD_CURRENT; _last_pub_rate =0;}

    //--------------------------------------------------------------
    /** Getters */
    string          symbol()    { return _symbol; }
    ENUM_TIMEFRAMES timeframe() { return _timeframe; }
    string          name()      { return _name; }
    datetime        getLastPublishTimestamp() { return _last_pub_rate; }
    /** Setters */
    void            setLastPublishTimestamp(datetime tmstmp) { _last_pub_rate = tmstmp; }

   //--------------------------------------------------------------
    /** Setup instrument with symbol and timeframe descriptions
     *  @param arg_symbol Symbol
     *  @param arg_timeframe Timeframe
     */
    void setup(string arg_symbol, ENUM_TIMEFRAMES arg_timeframe) {
        _symbol = arg_symbol;
        _timeframe = arg_timeframe;
        _name  = _symbol + "_" + GetTimeframeText(_timeframe);
        _last_pub_rate = 0;
    }

    //--------------------------------------------------------------
    /** Get last N MqlRates from this instrument (symbol-timeframe)
     *  @param rates Receives last 'count' rates
     *  @param count Number of requested rates
     *  @return Number of returned rates
     */
    int GetRates(MqlRates& rates[], int count) {
        // ensures that symbol is setup
        if(StringLen(_symbol) > 0) {
            return CopyRates(_symbol, _timeframe, 0, count, rates);
        }
        return 0;
    }

protected:
    string _name;                //!< Instrument descriptive name
    string _symbol;              //!< Symbol
    ENUM_TIMEFRAMES _timeframe;  //!< Timeframe
    datetime _last_pub_rate;     //!< Timestamp of the last published OHLC rate. Default = 0 (1 Jan 1970)

};

// Array of instruments whose rates will be published if Publish_MarketRates = True. It is initialized at OnInit() and
// can be updated through TRACK_RATES request from client peers.
Instrument Publish_Instruments[];



// VARIABLES FOR LATER
uchar _data[];
ZmqMsg request;

int g_reason = 0;

// Inform Client
void InformPullClient(Socket& pSocket, string message) {

   ZmqMsg pushReply(message);

   pSocket.send(pushReply,true); // NON-BLOCKING

}

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {

   EventSetMillisecondTimer(MILLISECOND_TIMER);     // Set Millisecond Timer to get client socket input
   
   context.setBlocky(false);
   
   if (g_reason != 3) {
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
   }
   return(INIT_SUCCEEDED);
}
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
   
   g_reason = reason;
   
   if (reason != 3){
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
   }

   EventKillTimer();
}
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   
   /*
      Use this OnTick() function to send market data to subscribed client.
   */
   OnTimer();
   lastUpdateMillis = GetTickCount();

   if(CheckServerStatus() == true) {
      // Python clients can subscribe to a price feed for each tracked symbol
      if(Publish_MarketData == true) {

        for(int s = 0; s < ArraySize(Publish_Symbols); s++) {

          string _tick = GetBidAsk(Publish_Symbols[s]);
          // only update if bid or ask changed.
          if (StringCompare(Publish_Symbols_LastTick[s], _tick) == 0) continue;
          Publish_Symbols_LastTick[s] = _tick;
          // add time current to send data
          _tick = TimeCurrent()+ ";" + _tick;
          // publish: topic=symbol msg=tick_data
          ZmqMsg reply(StringFormat("%s&%s", Publish_Symbols[s], _tick));
          //Print("Sending PRICE [" + reply.getData() + "] to PUB Socket");
          if(!pubSocket.send(reply, true)) {
            Print("###ERROR### Sending price");
          }
        }
      }

      // Python clients can also subscribe to a rates feed for each tracked instrument
      if(Publish_MarketRates == true) {
        for(int s = 0; s < ArraySize(Publish_Instruments); s++) {
            MqlRates curr_rate[];
            int count = Publish_Instruments[s].GetRates(curr_rate, 2);
            // if last rate is returned and its timestamp is greater than the last published...
            if(count > 0 && curr_rate[0].time > Publish_Instruments[s].getLastPublishTimestamp()) {
                // then send a new pub message with this new rate
                string _rates = StringFormat("%u;%f;%f;%f;%f;%d;%d;%d",
                                    curr_rate[0].time,
                                    curr_rate[0].open,
                                    curr_rate[0].high,
                                    curr_rate[0].low,
                                    curr_rate[0].close,
                                    curr_rate[0].tick_volume,
                                    curr_rate[0].spread,
                                    curr_rate[0].real_volume);
                ZmqMsg reply(StringFormat("%s&%s", Publish_Instruments[s].name(), _rates));
                Print("Sending Rates @"+TimeToStr(curr_rate[0].time) + " [" + reply.getData() + "] to PUB Socket");
                if(!pubSocket.send(reply, true)) {
                    Print("###ERROR### Sending rate");
                }
                // updates the timestamp
                Publish_Instruments[s].setLastPublishTimestamp(curr_rate[0].time);

          }
        }
      }
   }
   
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
      SplitMessage(dataStr, components, ";");

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

   // 1) Get Symbol

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
   if(compArray[0] == "GET_SYMBOL")
      switch_action = 1;
   if(compArray[0] == "HIST")
      switch_action = 2;
   if(compArray[0] == "DRAW")
      switch_action = 3;
   if(compArray[0] == "CLEAR")
      switch_action = 4;
   if(compArray[0] == "DELETE")
      switch_action = 5;
   if(compArray[0] == "TRACK_PRICES")
      switch_action = 6;
   if(compArray[0] == "TRACK_RATES")
      switch_action = 7;
   
   Print(compArray[0]);

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
            GetSymbol(zmq_ret);

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
            
            break;
            
         case 5: // Delete
            
            zmq_ret = "{";
            
            Delete(compArray, zmq_ret);
            
            InformPullClient(pSocket, zmq_ret + "}");
            
            break;
         
         case 6: // SETUP LIST OF SYMBOLS TO TRACK PRICES

            zmq_ret = "{";

            DWX_SetSymbolList(compArray, zmq_ret);

            InformPullClient(pSocket, zmq_ret + "}");

            break;

         case 7: // SETUP LIST OF INSTRUMENTS TO TRACK RATES

            zmq_ret = "{";

            DWX_SetInstrumentList(compArray, zmq_ret);

            InformPullClient(pSocket, zmq_ret + "}");

            break;
            
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

//+------------------------------------------------------------------+
// Set list of symbols to get real-time price data
void DWX_SetSymbolList(string& compArray[], string& zmq_ret) {
    
   zmq_ret = zmq_ret + "'_action': 'TRACK_PRICES'";
   
   // Format: TRACK_PRICES|SYMBOL_1|SYMBOL_2|...|SYMBOL_N
   string result = "Tracking PRICES from";
   string errorSymbols = "";
   int _num_symbols = ArraySize(compArray) - 1;
   if(_num_symbols > 0) {
      for(int s=0; s<_num_symbols; s++) {
         ArrayResize(Publish_Symbols, s+1);
         ArrayResize(Publish_Symbols_LastTick, s+1);
         Publish_Symbols[s] = compArray[s+1];
         result += " " + Publish_Symbols[s];
         
      }
      if (StringLen(errorSymbols) > 0)
         errorSymbols = "[" + StringSubstr(errorSymbols, 0, StringLen(errorSymbols)-2) + "]";
      else
         errorSymbols = "[]";
      zmq_ret = zmq_ret + ", '_data': {'symbol_count':" + IntegerToString(_num_symbols) + ", 'error_symbols':" + errorSymbols + "}";
      Publish_MarketData = true;
   } else {
      Publish_MarketData = false;
      ArrayResize(Publish_Symbols, 1);
      ArrayResize(Publish_Symbols_LastTick, 1);
      zmq_ret = zmq_ret + ", '_data': {'symbol_count': 0}";
      result += " NONE";
   }
   Print(result);
}


//+------------------------------------------------------------------+
// Set list of instruments to get OHLC rates
void DWX_SetInstrumentList(string& compArray[], string& zmq_ret) {

   zmq_ret = zmq_ret + "'_action': 'TRACK_RATES'";

   printArray(compArray);

   // Format: TRACK_RATES|SYMBOL_1|TIMEFRAME_1|SYMBOL_2|TIMEFRAME_2|...|SYMBOL_N|TIMEFRAME_N
   string result = "Tracking RATES from";
   string errorSymbols = "";
   int _num_instruments = (ArraySize(compArray) - 1)/2;
   if(_num_instruments > 0) {
      for(int s=0; s<_num_instruments; s++) {
         if (SymbolSelect(compArray[(2*s)+1], true)) {
            ArrayResize(Publish_Instruments, s+1);
            Publish_Instruments[s].setup(compArray[(2*s)+1], (ENUM_TIMEFRAMES)StrToInteger(compArray[(2*s)+2]));
            result += " " + Publish_Instruments[s].name();
         } else {
            errorSymbols += "'" + compArray[(2*s)+1] + "', ";
         }
      }
      if (StringLen(errorSymbols) > 0)
         errorSymbols = "[" + StringSubstr(errorSymbols, 0, StringLen(errorSymbols)-2) + "]";
      else
         errorSymbols = "[]";
      zmq_ret = zmq_ret + ", '_data': {'instrument_count':" + IntegerToString(_num_instruments) + ", 'error_symbols':" + errorSymbols + "}";
      Publish_MarketRates = true;
   } else {
      Publish_MarketRates = false;
      ArrayResize(Publish_Instruments, 1);
      zmq_ret = zmq_ret + ", '_data': {'instrument_count': 0}";
      result += " NONE";
   }
   Print(result);
}


int SplitMessage(string& message, string& retArray[], string sep){

   ushort u_sep = StringGetCharacter(sep,0);
   int splits = StringSplit(message, u_sep, retArray);
   return (splits);
   
}

void GetSymbol(string& zmq_ret){
   
   // Foramt: GET_SYMBOL
   zmq_ret = zmq_ret + "'_action': 'GET_SYMBOL', '_symbol': '" + ChartSymbol(0) + "'";
   
}


void GetSymbols(string& zmq_ret){
   
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


void Clear(string& zmq_ret){
   ObjectsDeleteAll();
}

void Delete(string& compArray[],string& zmq_ret) {

   int chart_id = StringToInteger(compArray[1]);
   string names[100];
   int cnt = SplitMessage(compArray[2], names, ",");
   
   bool total_success = True;
   
   for(int i=0; i<cnt; i++){
      if(!ObjectDelete(chart_id,names[i]))
        {
         Print(__FUNCTION__,
               ": failed to delete a trend line! Error code = ",GetLastError());
         total_success = False;
        }
   }
   
   if (total_success)
      zmq_ret = zmq_ret + ", '_result': 'Successed'";
   else
      zmq_ret = zmq_ret + ", '_result': 'Failed'";
}

void Draw(string& compArray[], string& zmq_ret){

   /* 
      compArray[1] : Type
      
      Types:
      VLine, HLine, TREND, ...
   */
   
   int switch_action = 0;
   zmq_ret = zmq_ret + "'_action': 'DRAW'";
   
   if(compArray[1] == "VLINE")
      switch_action = 1;
   if(compArray[1] == "HLINE")
      switch_action = 2;
   if(compArray[1] == "TREND")
      switch_action = 3;
   if(compArray[1] == "RECTANGLE")
      switch_action = 4;
   if(compArray[1] == "TRIANGLE")
      switch_action = 5;
   if(compArray[1] == "ELLIPSE")
      switch_action = 6;
   if(compArray[1] == "THUMBUP")
      switch_action = 7;
   if(compArray[1] == "THUMBDOWN")
      switch_action = 8;
   if(compArray[1] == "ARROWUP")
      switch_action = 9;
   if(compArray[1] == "ARROWDOWN")
      switch_action = 10;
   if(compArray[1] == "ARROWBUY")
      switch_action = 11;
   if(compArray[1] == "ARROWSELL")
      switch_action = 12;
   if(compArray[1] == "TEXT")
      switch_action = 13;
   if(compArray[1] == "LABEL")
      switch_action = 14;
   if(compArray[1] == "RECTLABEL")
      switch_action = 15;
   if(compArray[1] == "ARROW")
      switch_action = 16;
   
   bool success = false;  
   bool total_success = false; 
   
   string times1[100];
   string prices1[100];
   string times2[100];
   string prices2[100];
   string times3[100];
   string prices3[100];
   string scales[100];
   string text[100];
   string x1[100];
   string y1[100];
   string width[100];
   string height[100];
   string names[100];
   int cnt;
   
   switch(switch_action) {
         case 1: // VLINE
            // Foramt : ChartId | Name | SubWindow | Time | Color | Style | Width | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            
            cnt = SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[3], names, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = VLineCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StringToColor(compArray[6]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[7]),
                  StrToInteger(compArray[8]),
                  StrToInteger(compArray[9]), 
                  StrToInteger(compArray[10]), 
                  StrToInteger(compArray[11]), 
                  StrToInteger(compArray[12]));
                  
                  if(!success)
                     total_success = false;
            }
            
            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;

         case 2: //HLINE
            // Foramt : ChartId | Name | SubWindow | Price | Color | Style | Width | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            
            
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], prices1, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
            success = HLineCreate(
               StringToInteger(compArray[2]),
               names[i], 
               StrToInteger(compArray[4]),
               StrToDouble(prices1[i]),
               StringToColor(compArray[6]),
               (ENUM_LINE_STYLE)StrToInteger(compArray[7]),
               StrToInteger(compArray[8]),
               StrToInteger(compArray[9]), 
               StrToInteger(compArray[10]), 
               StrToInteger(compArray[11]), 
               StrToInteger(compArray[12]));
               if(!success)
                     total_success = false;
            }
            
            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";

            break;

         case 3: //TREND
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Time2 | Price2 | Color | Style | Width | Back | Selection | Ray | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            SplitMessage(compArray[7], times2, ",");
            SplitMessage(compArray[8], prices2, ",");
            
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = TrendCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  StrToTime(times2[i]),
                  StrToDouble(prices2[i]),
                  StringToColor(compArray[9]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[10]),
                  StrToInteger(compArray[11]),
                  StrToInteger(compArray[12]), 
                  StrToInteger(compArray[13]), 
                  StrToInteger(compArray[14]), 
                  StrToInteger(compArray[15]),
                  StrToInteger(compArray[16]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 4: //RECTANGLE
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Time2 | Price2 | Color | Style | Width | Fill | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            SplitMessage(compArray[7], times2, ",");
            SplitMessage(compArray[8], prices2, ",");
            
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = RectangleCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  StrToTime(times2[i]),
                  StrToDouble(prices2[i]),
                  StringToColor(compArray[9]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[10]),
                  StrToInteger(compArray[11]),
                  StrToInteger(compArray[12]), 
                  StrToInteger(compArray[13]), 
                  StrToInteger(compArray[14]), 
                  StrToInteger(compArray[15]),
                  StrToInteger(compArray[16]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 5: //TRIANGLE
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Time2 | Price2 | Time3 | Price3 | Color | Style | Width | Fill | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            SplitMessage(compArray[7], times2, ",");
            SplitMessage(compArray[8], prices2, ",");
            SplitMessage(compArray[9], times3, ",");
            SplitMessage(compArray[10], prices3, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = TriangleCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  StrToTime(times2[i]),
                  StrToDouble(prices2[i]),
                  StrToTime(times3[i]),
                  StrToDouble(prices3[i]),
                  StringToColor(compArray[11]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[12]),
                  StrToInteger(compArray[13]),
                  StrToInteger(compArray[14]), 
                  StrToInteger(compArray[15]), 
                  StrToInteger(compArray[16]), 
                  StrToInteger(compArray[17]),
                  StrToInteger(compArray[18]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 6: //ELLIPSE
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Time2 | Price2 | Scale | Color | Style | Width | Fill | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            SplitMessage(compArray[7], times2, ",");
            SplitMessage(compArray[8], prices2, ",");
            SplitMessage(compArray[9], scales, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = EllipseCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  StrToTime(times2[i]),
                  StrToDouble(prices2[i]),
                  StrToDouble(scales[i]),
                  StringToColor(compArray[10]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[11]),
                  StrToInteger(compArray[12]),
                  StrToInteger(compArray[13]), 
                  StrToInteger(compArray[14]), 
                  StrToInteger(compArray[15]), 
                  StrToInteger(compArray[16]),
                  StrToInteger(compArray[17]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 7: //THUMBUP
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = ArrowThumbUpCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  (ENUM_ARROW_ANCHOR)StrToInteger(compArray[7]),
                  StringToColor(compArray[8]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[9]),
                  StrToInteger(compArray[10]),
                  StrToInteger(compArray[11]), 
                  StrToInteger(compArray[12]), 
                  StrToInteger(compArray[13]), 
                  StrToInteger(compArray[14]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 8: //THUMBDOWN
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = ArrowThumbUpCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  (ENUM_ARROW_ANCHOR)StrToInteger(compArray[7]),
                  StringToColor(compArray[8]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[9]),
                  StrToInteger(compArray[10]),
                  StrToInteger(compArray[11]), 
                  StrToInteger(compArray[12]), 
                  StrToInteger(compArray[13]), 
                  StrToInteger(compArray[14]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 9: //ARROWUP
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = ArrowUpCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  (ENUM_ARROW_ANCHOR)StrToInteger(compArray[7]),
                  StringToColor(compArray[8]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[9]),
                  StrToInteger(compArray[10]),
                  StrToInteger(compArray[11]), 
                  StrToInteger(compArray[12]), 
                  StrToInteger(compArray[13]), 
                  StrToInteger(compArray[14]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 10: //ARROWDOWN
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = ArrowDownCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  (ENUM_ARROW_ANCHOR)StrToInteger(compArray[7]),
                  StringToColor(compArray[8]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[9]),
                  StrToInteger(compArray[10]),
                  StrToInteger(compArray[11]), 
                  StrToInteger(compArray[12]), 
                  StrToInteger(compArray[13]), 
                  StrToInteger(compArray[14]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 11: //ARROWBUY
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Color | Style | Width | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = ArrowBuyCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  StringToColor(compArray[7]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[8]),
                  StrToInteger(compArray[9]),
                  StrToInteger(compArray[10]), 
                  StrToInteger(compArray[11]), 
                  StrToInteger(compArray[12]), 
                  StrToInteger(compArray[13]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 12: //ARROWSELL
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | Color | Style | Width | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = ArrowSellCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  StringToColor(compArray[7]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[8]),
                  StrToInteger(compArray[9]),
                  StrToInteger(compArray[10]), 
                  StrToInteger(compArray[11]), 
                  StrToInteger(compArray[12]), 
                  StrToInteger(compArray[13]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 13: //TEXT
            // Foramt : ChartId | Name | SubWindow | Time | Price | Text | Font | FontSize | Color | Angle | Anchor | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            SplitMessage(compArray[7], text, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = TextCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  text[i],
                  compArray[8],
                  StrToInteger(compArray[9]),
                  StringToColor(compArray[10]),
                  StrToDouble(compArray[11]),
                  (ENUM_ANCHOR_POINT)StrToInteger(compArray[12]),
                  StrToInteger(compArray[13]), 
                  StrToInteger(compArray[14]), 
                  StrToInteger(compArray[15]), 
                  StrToInteger(compArray[16]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 14: //LABEL
            // Foramt : ChartId | Name | SubWindow | X | Y | Corner | Text | Font | FontSize | Color | Angle | Anchor | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], x1, ",");
            SplitMessage(compArray[6], y1, ",");
            SplitMessage(compArray[8], text, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = LabelCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToInteger(x1[i]),
                  StrToInteger(y1[i]),
                  (ENUM_BASE_CORNER)StrToInteger(compArray[7]),
                  text[i],
                  compArray[9],
                  StrToInteger(compArray[10]),
                  StringToColor(compArray[11]),
                  StrToDouble(compArray[12]),
                  (ENUM_ANCHOR_POINT)StrToInteger(compArray[13]),
                  StrToInteger(compArray[14]), 
                  StrToInteger(compArray[15]), 
                  StrToInteger(compArray[16]), 
                  StrToInteger(compArray[17]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 15: //RectLabel
            // Foramt : ChartId | Name | SubWindow | X | Y | Width | Height | BackColor | Border | Corner | Color | Style | LineWidth | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], x1, ",");
            SplitMessage(compArray[6], y1, ",");
            SplitMessage(compArray[7], width, ",");
            SplitMessage(compArray[8], height, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = RectLabelCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToInteger(x1[i]),
                  StrToInteger(y1[i]),
                  StrToInteger(width[i]),
                  StrToInteger(height[i]),
                  StringToColor(compArray[9]),
                  (ENUM_BORDER_TYPE)StrToInteger(compArray[10]),
                  (ENUM_BASE_CORNER)StrToInteger(compArray[11]),
                  StringToColor(compArray[12]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[13]),
                  StrToInteger(compArray[14]),
                  StrToInteger(compArray[15]), 
                  StrToInteger(compArray[16]), 
                  StrToInteger(compArray[17]), 
                  StrToInteger(compArray[18]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;
         
         case 16: //ARROW
            // Foramt : ChartId | Name | SubWindow | Time1 | Price1 | ArrowCode | Anchor | Color | Style | Width | Back | Selection | Hidden | ZOrder | Description
            // Function definition:
            cnt = SplitMessage(compArray[3], names, ",");
            SplitMessage(compArray[5], times1, ",");
            SplitMessage(compArray[6], prices1, ",");
            
            total_success = true;
            for(int i=0; i<cnt; i++){
               success = ArrowCreate(
                  StringToInteger(compArray[2]),
                  names[i], 
                  StrToInteger(compArray[4]),
                  StrToTime(times1[i]),
                  StrToDouble(prices1[i]),
                  StrToInteger(compArray[7]),
                  (ENUM_ARROW_ANCHOR)StrToInteger(compArray[8]),
                  StringToColor(compArray[9]),
                  (ENUM_LINE_STYLE)StrToInteger(compArray[10]),
                  StrToInteger(compArray[11]),
                  StrToInteger(compArray[12]), 
                  StrToInteger(compArray[13]), 
                  StrToInteger(compArray[14]), 
                  StrToInteger(compArray[15]));
                  
                  if(!success)
                     total_success = false;
            }

            if (total_success)
               zmq_ret = zmq_ret + ", '_result': 'Successed'";
            else
               zmq_ret = zmq_ret + ", '_result': 'Failed'";
            break;


         default:
            break;
      }
   
}

//+------------------------------------------------------------------+
//| Create the arrow                                                 |
//+------------------------------------------------------------------+
bool ArrowCreate(const long              chart_ID=0,           // chart's ID
                 const string            name="Arrow",         // arrow name
                 const int               sub_window=0,         // subwindow index
                 datetime                time=0,               // anchor point time
                 double                  price=0,              // anchor point price
                 const uchar             arrow_code=252,       // arrow code
                 const ENUM_ARROW_ANCHOR anchor=ANCHOR_BOTTOM, // anchor point position
                 const color             clr=clrRed,           // arrow color
                 const ENUM_LINE_STYLE   style=STYLE_SOLID,    // border line style
                 const int               width=3,              // arrow size
                 const bool              back=false,           // in the background
                 const bool              selection=true,       // highlight to move
                 const bool              hidden=true,          // hidden in the object list
                 const long              z_order=0,
                 const string            des="")            // priority for mouse click
  {

//--- reset the error value
   ResetLastError();
//--- create an arrow
   if(!ObjectCreate(chart_ID,name,OBJ_ARROW,sub_window,time,price))
     {
      Print(__FUNCTION__,
            ": failed to create an arrow! Error code = ",GetLastError());
      return(false);
     }
//--- set the arrow code
   ObjectSetInteger(chart_ID,name,OBJPROP_ARROWCODE,arrow_code);
//--- set anchor type
   ObjectSetInteger(chart_ID,name,OBJPROP_ANCHOR,anchor);
//--- set the arrow color
   ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
//--- set the border line style
   ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
//--- set the arrow's size
   ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
//--- display in the foreground (false) or background (true)
   ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
//--- enable (true) or disable (false) the mode of moving the arrow by mouse
//--- when creating a graphical object using ObjectCreate function, the object cannot be
//--- highlighted and moved by default. Inside this method, selection parameter
//--- is true by default making it possible to highlight and move the object
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
//--- hide (true) or display (false) graphical object name in the object list
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
//--- set the priority for receiving the event of a mouse click in the chart
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
//-- set the descritpion of object
   ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
//--- successful execution
   return(true);
  }

//+------------------------------------------------------------------+
//| Create rectangle label                                           |
//+------------------------------------------------------------------+
bool RectLabelCreate(const long             chart_ID=0,               // chart's ID
                     const string           name="RectLabel",         // label name
                     const int              sub_window=0,             // subwindow index
                     const int              x=0,                      // X coordinate
                     const int              y=0,                      // Y coordinate
                     const int              width=50,                 // width
                     const int              height=18,                // height
                     const color            back_clr=C'236,233,216',  // background color
                     const ENUM_BORDER_TYPE border=BORDER_SUNKEN,     // border type
                     const ENUM_BASE_CORNER corner=CORNER_LEFT_UPPER, // chart corner for anchoring
                     const color            clr=clrRed,               // flat border color (Flat)
                     const ENUM_LINE_STYLE  style=STYLE_SOLID,        // flat border style
                     const int              line_width=1,             // flat border width
                     const bool             back=false,               // in the background
                     const bool             selection=true,          // highlight to move
                     const bool             hidden=true,              // hidden in the object list
                     const long             z_order=0,
                     const string            des="")                // priority for mouse click
  {
//--- reset the error value
   ResetLastError();
//--- create a rectangle label
   if(!ObjectCreate(chart_ID,name,OBJ_RECTANGLE_LABEL,sub_window,0,0))
     {
      Print(__FUNCTION__,
            ": failed to create a rectangle label! Error code = ",GetLastError());
      return(false);
     }
//--- set label coordinates
   ObjectSetInteger(chart_ID,name,OBJPROP_XDISTANCE,x);
   ObjectSetInteger(chart_ID,name,OBJPROP_YDISTANCE,y);
//--- set label size
   ObjectSetInteger(chart_ID,name,OBJPROP_XSIZE,width);
   ObjectSetInteger(chart_ID,name,OBJPROP_YSIZE,height);
//--- set background color
   ObjectSetInteger(chart_ID,name,OBJPROP_BGCOLOR,back_clr);
//--- set border type
   ObjectSetInteger(chart_ID,name,OBJPROP_BORDER_TYPE,border);
//--- set the chart's corner, relative to which point coordinates are defined
   ObjectSetInteger(chart_ID,name,OBJPROP_CORNER,corner);
//--- set flat border color (in Flat mode)
   ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
//--- set flat border line style
   ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
//--- set flat border width
   ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,line_width);
//--- display in the foreground (false) or background (true)
   ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
//--- enable (true) or disable (false) the mode of moving the label by mouse
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
//--- hide (true) or display (false) graphical object name in the object list
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
//--- set the priority for receiving the event of a mouse click in the chart
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
//-- set the descritpion of object
   ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
//--- successful execution
   return(true);
  }


//+------------------------------------------------------------------+
//| Create a text label                                              |
//+------------------------------------------------------------------+
bool LabelCreate(const long              chart_ID=0,               // chart's ID
                 const string            name="Label",             // label name
                 const int               sub_window=0,             // subwindow index
                 const int               x=0,                      // X coordinate
                 const int               y=0,                      // Y coordinate
                 const ENUM_BASE_CORNER  corner=CORNER_LEFT_UPPER, // chart corner for anchoring
                 const string            text="Label",             // text
                 const string            font="Arial",             // font
                 const int               font_size=10,             // font size
                 const color             clr=clrRed,               // color
                 const double            angle=0.0,                // text slope
                 const ENUM_ANCHOR_POINT anchor=ANCHOR_LEFT_UPPER, // anchor type
                 const bool              back=false,               // in the background
                 const bool              selection=true,          // highlight to move
                 const bool              hidden=true,              // hidden in the object list
                 const long              z_order=0,
                 const string            des="")                // priority for mouse click
  {
   //--- reset the error value
      ResetLastError();
   //--- create a text label
      if(!ObjectCreate(chart_ID,name,OBJ_LABEL,sub_window,0,0))
        {
         Print(__FUNCTION__,
               ": failed to create text label! Error code = ",GetLastError());
         return(false);
        }
   //--- set label coordinates
      ObjectSetInteger(chart_ID,name,OBJPROP_XDISTANCE,x);
      ObjectSetInteger(chart_ID,name,OBJPROP_YDISTANCE,y);
   //--- set the chart's corner, relative to which point coordinates are defined
      ObjectSetInteger(chart_ID,name,OBJPROP_CORNER,corner);
   //--- set the text
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,text);
   //--- set text font
      ObjectSetString(chart_ID,name,OBJPROP_FONT,font);
   //--- set font size
      ObjectSetInteger(chart_ID,name,OBJPROP_FONTSIZE,font_size);
   //--- set the slope angle of the text
      ObjectSetDouble(chart_ID,name,OBJPROP_ANGLE,angle);
   //--- set anchor type
      ObjectSetInteger(chart_ID,name,OBJPROP_ANCHOR,anchor);
   //--- set color
      ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
   //--- display in the foreground (false) or background (true)
      ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
   //--- enable (true) or disable (false) the mode of moving the label by mouse
      ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
  }

//+------------------------------------------------------------------+
//| Creating Text object                                             |
//+------------------------------------------------------------------+
bool TextCreate(const long              chart_ID=0,               // chart's ID
                const string            name="Text",              // object name
                const int               sub_window=0,             // subwindow index
                datetime                time=0,                   // anchor point time
                double                  price=0,                  // anchor point price
                const string            text="Text",              // the text itself
                const string            font="Arial",             // font
                const int               font_size=10,             // font size
                const color             clr=clrRed,               // color
                const double            angle=0.0,                // text slope
                const ENUM_ANCHOR_POINT anchor=ANCHOR_LEFT_UPPER, // anchor type
                const bool              back=false,               // in the background
                const bool              selection=true,          // highlight to move
                const bool              hidden=true,              // hidden in the object list
                const long              z_order=0)                // priority for mouse click
  {
//--- reset the error value
   ResetLastError();
//--- create Text object
   if(!ObjectCreate(chart_ID,name,OBJ_TEXT,sub_window,time,price))
     {
      Print(__FUNCTION__,
            ": failed to create \"Text\" object! Error code = ",GetLastError());
      return(false);
     }
//--- set the text
   ObjectSetString(chart_ID,name,OBJPROP_TEXT,text);
//--- set text font
   ObjectSetString(chart_ID,name,OBJPROP_FONT,font);
//--- set font size
   ObjectSetInteger(chart_ID,name,OBJPROP_FONTSIZE,font_size);
//--- set the slope angle of the text
   ObjectSetDouble(chart_ID,name,OBJPROP_ANGLE,angle);
//--- set anchor type
   ObjectSetInteger(chart_ID,name,OBJPROP_ANCHOR,anchor);
//--- set color
   ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
//--- display in the foreground (false) or background (true)
   ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
//--- enable (true) or disable (false) the mode of moving the object by mouse
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
//--- hide (true) or display (false) graphical object name in the object list
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
//--- set the priority for receiving the event of a mouse click in the chart
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
//--- successful execution
   return(true);
  }

//+------------------------------------------------------------------+
//| Create Sell sign                                                 |
//+------------------------------------------------------------------+
bool ArrowSellCreate(const long            chart_ID=0,        // chart's ID
                     const string          name="ArrowSell",  // sign name
                     const int             sub_window=0,      // subwindow index
                     datetime              time=0,            // anchor point time
                     double                price=0,           // anchor point price
                     const color           clr=C'225,68,29',  // sign color
                     const ENUM_LINE_STYLE style=STYLE_SOLID, // line style (when highlighted)
                     const int             width=1,           // line size (when highlighted)
                     const bool            back=false,        // in the background
                     const bool            selection=false,   // highlight to move
                     const bool            hidden=true,       // hidden in the object list
                     const long            z_order=0,
                     const string            des="")         // priority for mouse click
  {

//--- reset the error value
   ResetLastError();
//--- create the sign
   if(!ObjectCreate(chart_ID,name,OBJ_ARROW_SELL,sub_window,time,price))
     {
      Print(__FUNCTION__,
            ": failed to create \"Sell\" sign! Error code = ",GetLastError());
      return(false);
     }
//--- set a sign color
   ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
//--- set a line style (when highlighted)
   ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
//--- set a line size (when highlighted)
   ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
//--- display in the foreground (false) or background (true)
   ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
//--- enable (true) or disable (false) the mode of moving the sign by mouse
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
//--- hide (true) or display (false) graphical object name in the object list
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
//--- set the priority for receiving the event of a mouse click in the chart
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
//-- set the descritpion of object
   ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
//--- successful execution
   return(true);
  }

//+------------------------------------------------------------------+
//| Create Buy sign                                                  |
//+------------------------------------------------------------------+
bool ArrowBuyCreate(const long            chart_ID=0,        // chart's ID
                    const string          name="ArrowBuy",   // sign name
                    const int             sub_window=0,      // subwindow index
                    datetime              time=0,            // anchor point time
                    double                price=0,           // anchor point price
                    const color           clr=C'3,95,172',   // sign color
                    const ENUM_LINE_STYLE style=STYLE_SOLID, // line style (when highlighted)
                    const int             width=1,           // line size (when highlighted)
                    const bool            back=false,        // in the background
                    const bool            selection=false,   // highlight to move
                    const bool            hidden=true,       // hidden in the object list
                    const long            z_order=0,
                    const string            des="")         // priority for mouse click
  {
   //--- reset the error value
      ResetLastError();
   //--- create the sign
      if(!ObjectCreate(chart_ID,name,OBJ_ARROW_BUY,sub_window,time,price))
        {
         Print(__FUNCTION__,
               ": failed to create \"Buy\" sign! Error code = ",GetLastError());
         return(false);
        }
   //--- set a sign color
      ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
   //--- set a line style (when highlighted)
      ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
   //--- set a line size (when highlighted)
      ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
   //--- display in the foreground (false) or background (true)
      ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
   //--- enable (true) or disable (false) the mode of moving the sign by mouse
      ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
  }

//+------------------------------------------------------------------+
//| Create Array Down sign                                           |
//+------------------------------------------------------------------+
bool ArrowDownCreate(const long              chart_ID=0,           // chart's ID
                     const string            name="ArrowDown",     // sign name
                     const int               sub_window=0,         // subwindow index
                     datetime                time=0,               // anchor point time
                     double                  price=0,              // anchor point price
                     const ENUM_ARROW_ANCHOR anchor=ANCHOR_BOTTOM, // anchor type
                     const color             clr=clrRed,           // sign color
                     const ENUM_LINE_STYLE   style=STYLE_SOLID,    // border line style
                     const int               width=3,              // sign size
                     const bool              back=false,           // in the background
                     const bool              selection=true,       // highlight to move
                     const bool              hidden=true,          // hidden in the object list
                     const long              z_order=0,
                     const string            des="")            // priority for mouse click
  {
   
   //--- reset the error value
      ResetLastError();
   //--- create the sign
      if(!ObjectCreate(chart_ID,name,OBJ_ARROW_DOWN,sub_window,time,price))
        {
         Print(__FUNCTION__,
               ": failed to create \"Arrow Down\" sign! Error code = ",GetLastError());
         return(false);
        }
   //--- anchor type
      ObjectSetInteger(chart_ID,name,OBJPROP_ANCHOR,anchor);
   //--- set a sign color
      ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
   //--- set the border line style
      ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
   //--- set the sign size
      ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
   //--- display in the foreground (false) or background (true)
      ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
   //--- enable (true) or disable (false) the mode of moving the sign by mouse
   //--- when creating a graphical object using ObjectCreate function, the object cannot be
   //--- highlighted and moved by default. Inside this method, selection parameter
   //--- is true by default making it possible to highlight and move the object
      ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
  }

//+------------------------------------------------------------------+
//| Create Array Up sign                                             |
//+------------------------------------------------------------------+
bool ArrowUpCreate(const long              chart_ID=0,           // chart's ID
                   const string            name="ArrowUp",       // sign name
                   const int               sub_window=0,         // subwindow index
                   datetime                time=0,               // anchor point time
                   double                  price=0,              // anchor point price
                   const ENUM_ARROW_ANCHOR anchor=ANCHOR_BOTTOM, // anchor type
                   const color             clr=clrRed,           // sign color
                   const ENUM_LINE_STYLE   style=STYLE_SOLID,    // border line style
                   const int               width=3,              // sign size
                   const bool              back=false,           // in the background
                   const bool              selection=true,       // highlight to move
                   const bool              hidden=true,          // hidden in the object list
                   const long              z_order=0,
                   const string            des="")            // priority for mouse click
  {
   
   //--- reset the error value
      ResetLastError();
   //--- create the sign
      if(!ObjectCreate(chart_ID,name,OBJ_ARROW_UP,sub_window,time,price))
        {
         Print(__FUNCTION__,
               ": failed to create \"Arrow Up\" sign! Error code = ",GetLastError());
         return(false);
        }
   //--- set anchor type
      ObjectSetInteger(chart_ID,name,OBJPROP_ANCHOR,anchor);
   //--- set a sign color
      ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
   //--- set the border line style
      ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
   //--- set the sign size
      ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
   //--- display in the foreground (false) or background (true)
      ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
   //--- enable (true) or disable (false) the mode of moving the sign by mouse
   //--- when creating a graphical object using ObjectCreate function, the object cannot be
   //--- highlighted and moved by default. Inside this method, selection parameter
   //--- is true by default making it possible to highlight and move the object
      ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
  }

//+------------------------------------------------------------------+
//| Create Thumbs Down sign                                          |
//+------------------------------------------------------------------+
bool ArrowThumbDownCreate(const long              chart_ID=0,           // chart's ID
                          const string            name="ThumbDown",     // sign name
                          const int               sub_window=0,         // subwindow index
                          datetime                time=0,               // anchor point time
                          double                  price=0,              // anchor point price
                          const ENUM_ARROW_ANCHOR anchor=ANCHOR_BOTTOM, // anchor type
                          const color             clr=clrRed,           // sign color
                          const ENUM_LINE_STYLE   style=STYLE_SOLID,    // border line style
                          const int               width=3,              // sign size
                          const bool              back=false,           // in the background
                          const bool              selection=true,       // highlight to move
                          const bool              hidden=true,          // hidden in the object list
                          const long              z_order=0,
                          const string            des="")            // priority for mouse click
  {
//--- reset the error value
   ResetLastError();
//--- create the sign
   if(!ObjectCreate(chart_ID,name,OBJ_ARROW_THUMB_DOWN,sub_window,time,price))
     {
      Print(__FUNCTION__,
            ": failed to create \"Thumbs Down\" sign! Error code = ",GetLastError());
      return(false);
     }
//--- set anchor type
   ObjectSetInteger(chart_ID,name,OBJPROP_ANCHOR,anchor);
//--- set a sign color
   ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
//--- set the border line style
   ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
//--- set the sign size
   ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
//--- display in the foreground (false) or background (true)
   ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
//--- enable (true) or disable (false) the mode of moving the sign by mouse
//--- when creating a graphical object using ObjectCreate function, the object cannot be
//--- highlighted and moved by default. Inside this method, selection parameter
//--- is true by default making it possible to highlight and move the object
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
//--- hide (true) or display (false) graphical object name in the object list
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
//--- set the priority for receiving the event of a mouse click in the chart
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
//-- set the descritpion of object
   ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
//--- successful execution
   return(true);
  }

//+------------------------------------------------------------------+
//| Create Thumbs Up sign                                            |
//+------------------------------------------------------------------+
bool ArrowThumbUpCreate(const long              chart_ID=0,           // chart's ID
                        const string            name="ThumbUp",       // sign name
                        const int               sub_window=0,         // subwindow index
                        datetime                time=0,               // anchor point time
                        double                  price=0,              // anchor point price
                        const ENUM_ARROW_ANCHOR anchor=ANCHOR_BOTTOM, // anchor type
                        const color             clr=clrRed,           // sign color
                        const ENUM_LINE_STYLE   style=STYLE_SOLID,    // border line style
                        const int               width=3,              // sign size
                        const bool              back=false,           // in the background
                        const bool              selection=true,       // highlight to move
                        const bool              hidden=true,          // hidden in the object list
                        const long              z_order=0,
                        const string            des="")            // priority for mouse click
  {
   //--- reset the error value
      ResetLastError();
   //--- create the sign
      if(!ObjectCreate(chart_ID,name,OBJ_ARROW_THUMB_UP,sub_window,time,price))
        {
         Print(__FUNCTION__,
               ": failed to create \"Thumbs Up\" sign! Error code = ",GetLastError());
         return(false);
        }
   //--- set anchor type
      ObjectSetInteger(chart_ID,name,OBJPROP_ANCHOR,anchor);
   //--- set a sign color
      ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
   //--- set the border line style
      ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
   //--- set the sign size
      ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
   //--- display in the foreground (false) or background (true)
      ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
   //--- enable (true) or disable (false) the mode of moving the sign by mouse
   //--- when creating a graphical object using ObjectCreate function, the object cannot be
   //--- highlighted and moved by default. Inside this method, selection parameter
   //--- is true by default making it possible to highlight and move the object
      ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
  }

//+------------------------------------------------------------------+
//| Create an ellipse by the given coordinates                       |
//+------------------------------------------------------------------+
bool EllipseCreate(const long            chart_ID=0,        // chart's ID
                   const string          name="Ellipse",    // ellipse name
                   const int             sub_window=0,      // subwindow index 
                   datetime              time1=0,           // first point time
                   double                price1=0,          // first point price
                   datetime              time2=0,           // second point time
                   double                price2=0,          // second point price
                   double                ellipse_scale=0,   // ellipse scale ratio 
                   const color           clr=clrRed,        // ellipse color
                   const ENUM_LINE_STYLE style=STYLE_SOLID, // style of ellipse lines
                   const int             width=1,           // width of ellipse lines
                   const bool            fill=false,        // filling ellipse with color
                   const bool            back=false,        // in the background
                   const bool            selection=true,    // highlight to move
                   const bool            hidden=true,       // hidden in the object list
                   const long            z_order=0,
                   const string            des="")         // priority for mouse click
  {

//--- reset the error value
   ResetLastError();
//--- create an ellipse by the given coordinates
   if(!ObjectCreate(chart_ID,name,OBJ_ELLIPSE,sub_window,time1,price1,time2,price2))
     {
      Print(__FUNCTION__,
            ": failed to create an ellipse! Error code = ",GetLastError());
      return(false);
     }
   //--- set ellipse scale ratio 
      ObjectSetDouble(chart_ID,name,OBJPROP_SCALE,ellipse_scale);
   //--- set an ellipse color
      ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
   //--- set style of ellipse lines
      ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
   //--- set width of ellipse lines
      ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
   //--- display in the foreground (false) or background (true)
      ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
   //--- enable (true) or disable (false) the mode of highlighting the ellipse for moving
   //--- when creating a graphical object using ObjectCreate function, the object cannot be
   //--- highlighted and moved by default. Inside this method, selection parameter
   //--- is true by default making it possible to highlight and move the object
      ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
  }

//+------------------------------------------------------------------+
//| Create triangle by the given coordinates                         |
//+------------------------------------------------------------------+
bool TriangleCreate(const long            chart_ID=0,        // chart's ID
                    const string          name="Triangle",   // triangle name
                    const int             sub_window=0,      // subwindow index 
                    datetime              time1=0,           // first point time
                    double                price1=0,          // first point price
                    datetime              time2=0,           // second point time
                    double                price2=0,          // second point price
                    datetime              time3=0,           // third point time
                    double                price3=0,          // third point price
                    const color           clr=clrRed,        // triangle color
                    const ENUM_LINE_STYLE style=STYLE_SOLID, // style of triangle lines
                    const int             width=1,           // width of triangle lines
                    const bool            fill=false,        // filling triangle with color
                    const bool            back=false,        // in the background
                    const bool            selection=true,    // highlight to move
                    const bool            hidden=true,       // hidden in the object list
                    const long            z_order=0,
                    const string            des="")         // priority for mouse click
  {
   //--- reset the error value
      ResetLastError();
   //--- create triangle by the given coordinates
      if(!ObjectCreate(chart_ID,name,OBJ_TRIANGLE,sub_window,time1,price1,time2,price2,time3,price3))
        {
         Print(__FUNCTION__,
               ": failed to create a triangle! Error code = ",GetLastError());
         return(false);
        }
   //--- set triangle color
      ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
   //--- set style of triangle lines
      ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
   //--- set width of triangle lines
      ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
   //--- display in the foreground (false) or background (true)
      ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
   //--- enable (true) or disable (false) the mode of highlighting the triangle for moving
   //--- when creating a graphical object using ObjectCreate function, the object cannot be
   //--- highlighted and moved by default. Inside this method, selection parameter
   //--- is true by default making it possible to highlight and move the object
      ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
  }

//+------------------------------------------------------------------+
//| Create rectangle by the given coordinates                        |
//+------------------------------------------------------------------+
bool RectangleCreate(const long            chart_ID=0,        // chart's ID
                     const string          name="Rectangle",  // rectangle name
                     const int             sub_window=0,      // subwindow index 
                     datetime              time1=0,           // first point time
                     double                price1=0,          // first point price
                     datetime              time2=0,           // second point time
                     double                price2=0,          // second point price
                     const color           clr=clrRed,        // rectangle color
                     const ENUM_LINE_STYLE style=STYLE_SOLID, // style of rectangle lines
                     const int             width=1,           // width of rectangle lines
                     const bool            fill=false,        // filling rectangle with color
                     const bool            back=true,        // in the background
                     const bool            selection=true,    // highlight to move
                     const bool            hidden=true,       // hidden in the object list
                     const long            z_order=0,
                     const string            des="")         // priority for mouse click
  {
   //--- reset the error value
      ResetLastError();
   //--- create a rectangle by the given coordinates
      if(!ObjectCreate(chart_ID,name,OBJ_RECTANGLE,sub_window,time1,price1,time2,price2))
        {
         Print(__FUNCTION__,
               ": failed to create a rectangle! Error code = ",GetLastError());
         return(false);
        }
   //--- set rectangle color
      ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
   //--- set the style of rectangle lines
      ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
   //--- set width of the rectangle lines
      ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
   //--- enable (true) or disable (false) the mode of filling the rectangle
      ObjectSetInteger(chart_ID,name,OBJPROP_FILL,fill);
   //--- display in the foreground (false) or background (true)
      ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
   //--- enable (true) or disable (false) the mode of highlighting the rectangle for moving
   //--- when creating a graphical object using ObjectCreate function, the object cannot be
   //--- highlighted and moved by default. Inside this method, selection parameter
   //--- is true by default making it possible to highlight and move the object
      ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
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
                 const long            z_order=0,
                 const string            des="")         // priority for mouse click
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
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
}

bool HLineCreate(const long            chart_ID=0,        // chart's ID
                 const string          name="HLine",      // line name
                 const int             sub_window=0,      // subwindow index
                 double                price=0,           // line price
                 const color           clr=clrRed,        // line color
                 const ENUM_LINE_STYLE style=STYLE_SOLID, // line style
                 const int             width=1,           // line width
                 const bool            back=false,        // in the background
                 const bool            selection=true,    // highlight to move
                 const bool            hidden=true,       // hidden in the object list
                 const long            z_order=0,
                 const string            des="")         // priority for mouse click
  {
   //--- if the price is not set, set it at the current Bid price level
      if(!price)
         price=SymbolInfoDouble(Symbol(),SYMBOL_BID);
   //--- reset the error value
      ResetLastError();
   //--- create a horizontal line
      if(!ObjectCreate(chart_ID,name,OBJ_HLINE,sub_window,0,price))
        {
         Print(__FUNCTION__,
               ": failed to create a horizontal line! Error code = ",GetLastError());
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
   //--- hide (true) or display (false) graphical object name in the object list
      ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
   //--- set the priority for receiving the event of a mouse click in the chart
      ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
   //-- set the descritpion of object
      ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
   //--- successful execution
      return(true);
}

bool TrendCreate(const long            chart_ID=0,        // chart's ID
                 const string          name="TrendLine",  // line name
                 const int             sub_window=0,      // subwindow index
                 datetime              time1=0,           // first point time
                 double                price1=0,          // first point price
                 datetime              time2=0,           // second point time
                 double                price2=0,          // second point price
                 const color           clr=clrRed,        // line color
                 const ENUM_LINE_STYLE style=STYLE_SOLID, // line style
                 const int             width=1,           // line width
                 const bool            back=false,        // in the background
                 const bool            selection=true,    // highlight to move
                 const bool            ray_right=false,   // line's continuation to the right
                 const bool            hidden=true,       // hidden in the object list
                 const long            z_order=0,
                 const string            des="")         // priority for mouse click
  {
//--- reset the error value
   ResetLastError();
//--- create a trend line by the given coordinates
   if(!ObjectCreate(chart_ID,name,OBJ_TREND,sub_window,time1,price1,time2,price2))
     {
      Print(__FUNCTION__,
            ": failed to create a trend line! Error code = ",GetLastError());
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
//--- enable (true) or disable (false) the mode of continuation of the line's display to the right
   ObjectSetInteger(chart_ID,name,OBJPROP_RAY_RIGHT,ray_right);
//--- hide (true) or display (false) graphical object name in the object list
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
//--- set the priority for receiving the event of a mouse click in the chart
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
//-- set the descritpion of object
   ObjectSetString(chart_ID,name,OBJPROP_TEXT,des);
//--- successful execution
   return(true);
  }


//+------------------------------------------------------------------+
// Get Timeframe from text
string GetTimeframeText(ENUM_TIMEFRAMES tf) {
    // Standard timeframes
    switch(tf) {
        case PERIOD_M1:    return "M1";
        case PERIOD_M5:    return "M5";
        case PERIOD_M15:   return "M15";
        case PERIOD_M30:   return "M30";
        case PERIOD_H1:    return "H1";
        case PERIOD_H4:    return "H4";
        case PERIOD_D1:    return "D1";
        case PERIOD_W1:    return "W1";
        case PERIOD_MN1:   return "MN1";
        default:           return "UNKNOWN";
    }
}

bool CheckServerStatus() {

   // Is _StopFlag == True, inform the client application
   if (IsStopped()) {
      InformPullClient(pullSocket, "{'_response': 'EA_IS_STOPPED'}");
      return(false);
   }
   
   // Default
   return(true);
}

string ErrorDescription(int error_code) {
   string error_string;
//----
   switch(error_code)
     {
      //---- codes returned from trade server
      case 0:
      case 1:   error_string="no error";                                                  break;
      case 2:   error_string="common error";                                              break;
      case 3:   error_string="invalid trade parameters";                                  break;
      case 4:   error_string="trade server is busy";                                      break;
      case 5:   error_string="old version of the client terminal";                        break;
      case 6:   error_string="no connection with trade server";                           break;
      case 7:   error_string="not enough rights";                                         break;
      case 8:   error_string="too frequent requests";                                     break;
      case 9:   error_string="malfunctional trade operation (never returned error)";      break;
      case 64:  error_string="account disabled";                                          break;
      case 65:  error_string="invalid account";                                           break;
      case 128: error_string="trade timeout";                                             break;
      case 129: error_string="invalid price";                                             break;
      case 130: error_string="invalid stops";                                             break;
      case 131: error_string="invalid trade volume";                                      break;
      case 132: error_string="market is closed";                                          break;
      case 133: error_string="trade is disabled";                                         break;
      case 134: error_string="not enough money";                                          break;
      case 135: error_string="price changed";                                             break;
      case 136: error_string="off quotes";                                                break;
      case 137: error_string="broker is busy (never returned error)";                     break;
      case 138: error_string="requote";                                                   break;
      case 139: error_string="order is locked";                                           break;
      case 140: error_string="long positions only allowed";                               break;
      case 141: error_string="too many requests";                                         break;
      case 145: error_string="modification denied because order too close to market";     break;
      case 146: error_string="trade context is busy";                                     break;
      case 147: error_string="expirations are denied by broker";                          break;
      case 148: error_string="amount of open and pending orders has reached the limit";   break;
      case 149: error_string="hedging is prohibited";                                     break;
      case 150: error_string="prohibited by FIFO rules";                                  break;
      //---- mql4 errors
      case 4000: error_string="no error (never generated code)";                          break;
      case 4001: error_string="wrong function pointer";                                   break;
      case 4002: error_string="array index is out of range";                              break;
      case 4003: error_string="no memory for function call stack";                        break;
      case 4004: error_string="recursive stack overflow";                                 break;
      case 4005: error_string="not enough stack for parameter";                           break;
      case 4006: error_string="no memory for parameter string";                           break;
      case 4007: error_string="no memory for temp string";                                break;
      case 4008: error_string="not initialized string";                                   break;
      case 4009: error_string="not initialized string in array";                          break;
      case 4010: error_string="no memory for array\' string";                             break;
      case 4011: error_string="too long string";                                          break;
      case 4012: error_string="remainder from zero divide";                               break;
      case 4013: error_string="zero divide";                                              break;
      case 4014: error_string="unknown command";                                          break;
      case 4015: error_string="wrong jump (never generated error)";                       break;
      case 4016: error_string="not initialized array";                                    break;
      case 4017: error_string="dll calls are not allowed";                                break;
      case 4018: error_string="cannot load library";                                      break;
      case 4019: error_string="cannot call function";                                     break;
      case 4020: error_string="expert function calls are not allowed";                    break;
      case 4021: error_string="not enough memory for temp string returned from function"; break;
      case 4022: error_string="system is busy (never generated error)";                   break;
      case 4050: error_string="invalid function parameters count";                        break;
      case 4051: error_string="invalid function parameter value";                         break;
      case 4052: error_string="string function internal error";                           break;
      case 4053: error_string="some array error";                                         break;
      case 4054: error_string="incorrect series array using";                             break;
      case 4055: error_string="custom indicator error";                                   break;
      case 4056: error_string="arrays are incompatible";                                  break;
      case 4057: error_string="global variables processing error";                        break;
      case 4058: error_string="global variable not found";                                break;
      case 4059: error_string="function is not allowed in testing mode";                  break;
      case 4060: error_string="function is not confirmed";                                break;
      case 4061: error_string="send mail error";                                          break;
      case 4062: error_string="string parameter expected";                                break;
      case 4063: error_string="integer parameter expected";                               break;
      case 4064: error_string="double parameter expected";                                break;
      case 4065: error_string="array as parameter expected";                              break;
      case 4066: error_string="requested history data in update state";                   break;
      case 4099: error_string="end of file";                                              break;
      case 4100: error_string="some file error";                                          break;
      case 4101: error_string="wrong file name";                                          break;
      case 4102: error_string="too many opened files";                                    break;
      case 4103: error_string="cannot open file";                                         break;
      case 4104: error_string="incompatible access to a file";                            break;
      case 4105: error_string="no order selected";                                        break;
      case 4106: error_string="unknown symbol";                                           break;
      case 4107: error_string="invalid price parameter for trade function";               break;
      case 4108: error_string="invalid ticket";                                           break;
      case 4109: error_string="trade is not allowed in the expert properties";            break;
      case 4110: error_string="longs are not allowed in the expert properties";           break;
      case 4111: error_string="shorts are not allowed in the expert properties";          break;
      case 4200: error_string="object is already exist";                                  break;
      case 4201: error_string="unknown object property";                                  break;
      case 4202: error_string="object is not exist";                                      break;
      case 4203: error_string="unknown object type";                                      break;
      case 4204: error_string="no object name";                                           break;
      case 4205: error_string="object coordinates error";                                 break;
      case 4206: error_string="no specified subwindow";                                   break;
      default:   error_string="unknown error";
      }
   return(error_string);
}

//+------------------------------------------------------------------+

double DWX_GetAsk(string symbol) {
   if(symbol == "NULL") {
      return(Ask);
   } else {
      return(MarketInfo(symbol,MODE_ASK));
   }
}

//+------------------------------------------------------------------+

double DWX_GetBid(string symbol) {
   if(symbol == "NULL") {
      return(Bid);
   } else {
      return(MarketInfo(symbol,MODE_BID));
   }
}

//+------------------------------------------------------------------+
// Generate string for Bid/Ask by symbol
string GetBidAsk(string symbol) {

   MqlTick last_tick;

   if(SymbolInfoTick(symbol,last_tick)) {
       return(StringFormat("%f;%f", last_tick.bid, last_tick.ask));
   }

   // Default
   return "";
   
}

void printArray(string &arr[]) {
   if (ArraySize(arr) == 0) Print("{}");
   string printStr = "{";
   int i;
   for (i=0; i<ArraySize(arr); i++) {
      if (i == ArraySize(arr)-1) printStr += arr[i];
      else printStr += arr[i] + ", ";
   }
   Print(printStr + "}");
}

//+------------------------------------------------------------------+
