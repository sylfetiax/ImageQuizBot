# ImageQuizBot
Telegram bot with a game against YOLOv8n model where you have to guess the figure in the picture. Also you can send your own picture and bot will respond you with model's predictions.

In this game, the AI model is a pre-trained YOLOv8 nano image classifier. It was fine-tuned on similar images but has never seen the specific images that will be used in the game. You can expect high accuracy from the model due to its state-of-the-art design.

[Telegram bot link](https://t.me/image_quiz_bot) (The bot is not hosted, so it only works when the script is running)

Model was trained on this [dataset](https://www.kaggle.com/datasets/frobert/handdrawn-shapes-hds-dataset).

If you want to test the model's performance on your own, just choose the 'Predict Figure' option and send a photo. You will receive predicted probabilities indicating which figure is in the picture you sent.

In the future, this bot may be updated to include more various and complex kinds of games. Feel free to reach out if you have any questions or ideas regarding this bot. I'm open to suggestions and feedback:)


