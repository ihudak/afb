import telepot


token = '7122941972:AAEW9PlaO7mhMr7LVxrbuiWC01s-okwpYa8' # telegram token
receiver_id = 369394004 # https://api.telegram.org/bot<TOKEN>/getUpdates


bot = telepot.Bot(token)

bot.sendMessage(receiver_id, 'This is a automated test message.') # send a activation message to telegram receiver id