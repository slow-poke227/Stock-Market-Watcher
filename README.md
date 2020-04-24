# Stock-Market-Watcher
Follow an equity with a visual LED representation using a few LEDs and a raspberry pi!

The light sequence is as follows:
Round 1 (current trend of stock): 0 (green/up), 1 (yellow/error), 2 (red/down)
Round 2 (current value compared to close): 0 (green/positive), 1 (yellow/error), 2 (red/negative)
Round 3 (current value compared to goal): 0 (green/above goal), 1 (yellow/error), 2 (red/below goal)

A few things to note:
  The API can only be called once every minute
  The project was written for python3, please ensure your RPi is up to date
