def unblock_user_subject(name: str) -> str:
    return f'{name}, ваш аккаунт в TaskService разблокирован'


def unblock_user_body(name: str) -> str:
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
            border-bottom: 2px solid #e6f0e6;
            padding-bottom: 20px;
        }}
        .header h1 {{
            font-size: 26px;
            color: #1a2b3c;
            margin: 0;
        }}
        .header .icon {{
            font-size: 48px;
            display: block;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 24px 0;
            color: #2c3e50;
            line-height: 1.7;
            font-size: 16px;
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
            color: #2e7d32;
            font-weight: 600;
        }}
        .button {{
            display: inline-block;
            background: #2a7de1;
            color: white;
            padding: 12px 28px;
            text-decoration: none;
            border-radius: 8px;
            margin: 8px 0 4px;
            font-weight: 500;
        }}
        .button:hover {{
            background: #1a5fb0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="icon">🔓</span>
            <h1>Аккаунт разблокирован</h1>
        </div>

        <div class="content">
            <p>Здравствуйте, <strong>{name}</strong>!</p>

            <p>
                Ваш аккаунт в <span class="highlight">TaskService</span> был 
                <strong>разблокирован</strong>.
            </p>

            <p>Вы снова можете пользоваться всеми функциями сервиса.</p>

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
