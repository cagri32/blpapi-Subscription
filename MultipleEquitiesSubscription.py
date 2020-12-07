# SimpleSubscriptionExample.py
from __future__ import print_function
from __future__ import absolute_import

import blpapi
import time
from optparse import OptionParser


def parseCmdLine():
    parser = OptionParser(description="Retrieve realtime data.")
    parser.add_option("-a",
                      "--ip",
                      dest="host",
                      help="server name or IP (default: %default)",
                      metavar="ipAddress",
                      default="localhost")
    parser.add_option("-p",
                      dest="port",
                      type="int",
                      help="server port (default: %default)",
                      metavar="tcpPort",
                      default=8194)
    parser.add_option("--me",
                      dest="maxEvents",
                      type="int",
                      help="stop after this many events (default: %default)",
                      metavar="maxEvents",
                      default=1000000)

    (options, args) = parser.parse_args()

    return options


def main():
    options = parseCmdLine()

    # Fill SessionOptions
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost(options.host)
    sessionOptions.setServerPort(options.port)

    print("Connecting to %s:%d" % (options.host, options.port))

    # Create a Session
    session = blpapi.Session(sessionOptions)

    # Start a Session
    if not session.start():
        print("Failed to start session.")
        return

    if not session.openService("//blp/mktdata"):
        print("Failed to open //blp/mktdata")
        return

    ### Use this list for writing the equity names manually
    equityNames = ["CVE CN Equity", "N CN Equity", "IBM US Equity", "CM CN Equity", "CM CT Equity"]# take name of the equities from a file as strings    
    
    ### Use this function for pulling the equity names from the input file
  # with open('input.txt') as f:
  #     equityNames2 = f.readlines()
  # equityNames = [x.strip() for x in equityNames2]
  # equity = {} 
    ###
    
    subscriptions = blpapi.SubscriptionList()
    
    for i in range(len(equityNames)):
        equity[equityNames[i]] = {'BID': "0.0", 'ASK': "0.0", 'VWAP': "0.0", 'TIME': "0.0" }
        subscriptions.add(equityNames[i],
                      "BID,ASK, VWAP, TIME",
                      "",
                      blpapi.CorrelationId(equityNames[i]))
        
    session.subscribe(subscriptions)

    try:
        # Process received events
        eventCount = 0
        while(True):
            # We provide timeout to give the chance to Ctrl+C handling:
            event = session.nextEvent(500)
            for msg in event:
                if (event.eventType() == blpapi.Event.SUBSCRIPTION_STATUS 
                        and msg.messageType() == "SubscriptionFailure"):
                   #msg.correlationIds()[0].value().find("Failure")!=-1
                    f = open("BadSubscription.txt", "a+")
                    s = ""
                    if msg.getElement("reason").getElement("errorCode").getValueAsInteger() !=12:
                        s = msg.toString()
                    f.write(s)

                elif event.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
                    print("--------- UPDATE ----------\n")
                    
                    oneEquity = msg.correlationIds()[0].value()  
                    
                    # Check and update if the newly arrived message has any updates for the following fields                    
                    if msg.hasElement("BID"):
                        equity[oneEquity]['BID'] = msg.getElement("BID").getValueAsFloat()
                    if msg.hasElement("ASK"):
                        equity[oneEquity]['ASK'] = msg.getElement("ASK").getValueAsFloat()
                    if msg.hasElement("VWAP"):
                        equity[oneEquity]['VWAP'] = msg.getElement("VWAP").getValueAsFloat()
                    if msg.hasElement("TIME"):
                        equity[oneEquity]['TIME'] = msg.getElement("TIME").getValueAsString()
                
                    # Print the updated Equity with all fields
                    
                    print(" Security: " + oneEquity +
                    "\n Bid:  " + str(equity[oneEquity]['BID']) +
                    "\n Ask:  " + str(equity[oneEquity]['ASK']))
                    diff = equity[oneEquity]['ASK'] - equity[oneEquity]['BID']
                    print(" Diff: %.5f" % diff)
                    
                    # If Ask-Bid difference is normal (0 or positive), print OK
                    if(diff >= 0):
                        print(" OK \n")
                    # If Ask-Bid difference is negative, print BAD and write the necessary info to a file
                    else:
                        print("BAD")
                    
                    print("\n Vwap: " + str(equity[oneEquity]['VWAP']))
                    print(" Time: "+ equity[oneEquity]['TIME'])
                    
                    # If time stamp is Null, print BAD and write the necessary info to a file
                    if(equity[oneEquity]['TIME'] is None):
                        print("BAD")
                    else:
                        print(" OK \n")
                    
                else:
                    print(msg)
                    print(msg.messageType())
            if event.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
                eventCount += 1
                if eventCount >= options.maxEvents:
                    break
    finally:
        # Stop the session
        session.stop()

if __name__ == "__main__":
    print("SimpleSubscriptionExample")
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C pressed. Stopping...")

__copyright__ = """
Copyright 2012. Bloomberg Finance L.P.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:  The above
copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
