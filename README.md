# blpapi-Subscription
I wrote this program to check the subscription function of Bloomberg and create automated report when a feed issue occurs.

The check analyzes 3 values.

First analysis is done with BID and ASK values.
BID must always be less than ASK.
If ASK-BID <= 0 then there is a feed issue at Bloomberg and that issue needs to be taken care of.

The second analysis is the VWAP value check.
The time stamp of VWAP is checked if the value is Null.
If there is not a valid time stamp, that is another feed issue to be fixed.
