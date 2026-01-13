# Інструкція з розгортання Trexim на Railway.app

## Чому Railway?

- **Надійність**: Стабільна робота без "засинання" серверів
- **Простота**: Автоматичне розгортання з GitHub
- **Ціна**: ~$5/місяць за стабільний сервіс
- **SSL**: Автоматичний HTTPS сертифікат
- **Домени**: Легке підключення custom domain (trexim.ai)

## Крок 1: Створення акаунту на Railway

1. Перейдіть на https://railway.app
2. Натисніть "Start a New Project"
3. Увійдіть через GitHub
4. Дозвольте Railway доступ до ваших репозиторіїв

## Крок 2: Створення проекту

1. Натисніть "New Project"
2. Оберіть "Deploy from GitHub repo"
3. Оберіть репозиторій `Taras732/trexim_v4`
4. Railway автоматично виявить Python проект

## Крок 3: Налаштування змінних середовища

У Railway dashboard:

1. Перейдіть у Settings → Variables
2. Додайте наступні змінні:

```
APP_ENV=production
ADMIN_PASSWORD=your_secure_password_here
```

**Важливо**: Змініть `your_secure_password_here` на безпечний пароль для адмін-панелі!

## Крок 4: Налаштування команди запуску

Railway автоматично використає `Procfile`, але якщо потрібно змінити:

1. Settings → Deploy
2. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Крок 5: Перший деплой

1. Railway автоматично почне білд після підключення репозиторію
2. Дочекайтеся завершення (2-3 хвилини)
3. Отримаєте URL типу: `https://trexim-v4-production.up.railway.app`
4. Перевірте, що сайт працює

## Крок 6: Підключення домену trexim.ai

### A. Додавання домену в Railway

1. Перейдіть у Settings → Domains
2. Натисніть "Add Domain"
3. Введіть `trexim.ai`
4. Railway покаже записи для налаштування DNS

### B. Налаштування DNS

У вашого реєстратора домену (де купили trexim.ai):

**Варіант 1: CNAME (рекомендовано)**
```
Type: CNAME
Name: www
Value: trexim-v4-production.up.railway.app
TTL: 3600

Type: CNAME
Name: @
Value: trexim-v4-production.up.railway.app
TTL: 3600
```

**Варіант 2: A Record**
Railway покаже IP адресу в налаштуваннях домену - використайте її:
```
Type: A
Name: @
Value: [IP від Railway]
TTL: 3600

Type: CNAME
Name: www
Value: trexim.ai
TTL: 3600
```

### C. Очікування propagation

- DNS зміни можуть зайняти 5-60 хвилин
- Перевірити статус: https://dnschecker.org/#A/trexim.ai
- Railway автоматично додасть SSL сертифікат після propagation

## Крок 7: Налаштування автоматичного деплою

Railway автоматично розгортає при push в main:

1. Settings → Triggers
2. Переконайтеся, що увімкнено "Auto Deploy"
3. Гілка: `main`

Тепер кожен `git push origin main` буде автоматично оновлювати сайт!

## Моніторинг та логи

### Перегляд логів
1. Перейдіть у вкладку "Deployments"
2. Оберіть останній deployment
3. Вкладка "View Logs"

### Метрики
1. Вкладка "Metrics"
2. Показує CPU, RAM, Network використання

## Вартість

Railway має pricing моделі:

- **Developer Plan**: $5/місяць включає:
  - $5 кредитів
  - ~500 годин роботи сервісу
  - Достатньо для малого/середнього трафіку

- **Team Plan**: $20/місяць
  - $20 кредитів
  - Для більшого трафіку

Перевірити використання: Dashboard → Usage

## Альтернативні варіанти розгортання

Якщо Railway не підходить:

### 1. DigitalOcean App Platform ($5/міс)
- Більш професійний
- Надійна інфраструктура
- https://cloud.digitalocean.com/apps

### 2. Fly.io ($5-10/міс)
- Гарний безкоштовний tier
- Глобальні edge locations
- https://fly.io

### 3. AWS Lightsail ($5/міс)
- Найбільш масштабований
- Складніше налаштування
- https://aws.amazon.com/lightsail/

### 4. VPS (DigitalOcean Droplet, Linode)
- Повний контроль
- Потребує більше налаштувань
- $4-6/місяць

## Troubleshooting

### Сервіс не запускається
1. Перевірте логи в Railway dashboard
2. Переконайтеся, що змінні середовища встановлені
3. Перевірте, що Procfile правильний

### 500 Internal Server Error
1. Перевірте логи - там буде traceback
2. Можливо проблема з шляхами до файлів
3. Перевірте, що всі залежності в requirements.txt

### Домен не працює
1. Перевірте DNS записи: https://dnschecker.org
2. Зачекайте 24-48 годин для повної propagation
3. Перевірте, що домен додано в Railway Settings → Domains

### CSS/JS не завантажуються
1. Перевірте, що static директорія існує
2. Перевірте логи на помилки при монтуванні StaticFiles
3. Переконайтеся, що шляхи в templates правильні

## Контакти для підтримки

- Railway документація: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/Taras732/trexim_v4/issues

---

**Примітка**: Цей проект вже налаштований з усіма необхідними файлами (Procfile, railway.json, runtime.txt). Просто слідуйте інструкціям вище!
