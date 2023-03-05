# Forex Trading Bots
Forex Trading Bots is a platform that allows users to create and execute custom trading strategies and indicators in the MetaTrader 4 (MT4) application. The project uses socket programming with ZMQ library to connect the Python and MQL4 processes.

# Features
Create custom trading strategies and indicators using Python.
Use well-known indicators such as channel detection, Elliot, harmonic patterns, and more.
Automatically trade using pre-defined strategies with relatively good profits.
Use the MetaTrader 4 (MT4) application for executing trades.
Use ZMQ library for socket programming and interprocess communication.
Use config files to choose which indicators or strategies to run in MT4.
# Installation
Install Python 3 on your machine. You can download the latest version from the official Python website https://www.python.org/downloads/.
Install the required packages using pip. You can install the packages by running the following command in your terminal:

```pip install -r requirements.txt```

Install the MetaTrader 4 (MT4) application on your machine. You can download the MT4 application from the official MetaQuotes website https://www.metaquotes.net/en/metatrader4.
# Usage
Open the MT4 application and navigate to the "Experts" tab.
Start the "Expert Advisor" by clicking on the "Auto Trading" button. 

Run the following command in your terminal to start the Python script:

```python launcher.py```

Choose which indicators or strategies to run by modifying the config files.
# Contributing
If you want to contribute to Forex Trading Bots, please fork the repository and submit a pull request. We welcome contributions of all kinds, including bug fixes, new features, and documentation improvements.

# License
Forex Trading Bots is licensed under the MIT License. See LICENSE for more information.

# Acknowledgments
Forex Trading Bots was inspired by the need for a flexible platform for creating custom trading strategies and indicators. We would like to thank the open source community for providing the tools and libraries that made this project possible.
