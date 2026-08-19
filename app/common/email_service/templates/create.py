def create_user_subject(name: str) -> str:
    return f'{name}, добро пожаловать в TaskService!'


def create_user_body(name: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskService</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f6f9fc;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 40px 30px;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #eef2f7;
            padding-bottom: 20px;
        }}
        .header h1 {{
            font-size: 26px;
            color: #1a2b3c;
            margin: 0;
        }}
        .content {{
            padding: 24px 0;
            color: #2c3e50;
            line-height: 1.7;
            font-size: 16px;
        }}
        .content ul {{
            padding-left: 20px;
            margin: 16px 0;
        }}
        .content ul li {{
            margin-bottom: 8px;
        }}
        .footer {{
            text-align: center;
            font-size: 13px;
            color: #8899aa;
            border-top: 1px solid #eef2f7;
            padding-top: 20px;
            margin-top: 10px;
        }}
        .highlight {{
            color: #2a7de1;
            font-weight: 600;
        }}
        .emoji {{
            font-size: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1></span> Добро пожаловать в TaskService!</h1>
        </div>

        <div class="content">
            <p>Здравствуйте, <strong>{name}</strong>!</p>

            <p>Рады видеть вас в <span class="highlight">TaskService</span> — 
            вашем персональном помощнике для управления задачами.</p>

            <p><strong>Вас ждет:</strong></p>
            <ul>
                <li>Создавайте задачи в несколько кликов</li>
                <li>Отслеживайте статус и прогресс</li>
                <li>Редактируйте и удаляйте задачи</li>
                <li>Управляйте профилем и настройками</li>
            </ul>

            <p>Начните прямо сейчас и сделайте свою работу продуктивнее!</p>

            <p>С уважением,<br><strong>Команда TaskService</strong></p>
        </div>

        <div class="footer">
            <p>Это письмо было отправлено автоматически.<br>Пожалуйста, не отвечайте на него.</p>
            <p>©TaskService</p>
        </div>
    </div>
</body>
</html>
"""
