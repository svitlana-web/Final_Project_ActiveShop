# Словарь данных

## customers.csv

| Поле | Описание |
|---|---|
| customer_id | ID клиента |
| signup_date | Дата регистрации |
| age | Возраст |
| gender | Пол |
| city | Город |
| region | Регион |
| acquisition_channel | Канал первого привлечения |
| loyalty_level | Уровень лояльности |
| ab_group | A/B-группа клиента |

## products.csv

| Поле | Описание |
|---|---|
| product_id | ID товара |
| product_name | Название |
| category | Категория |
| brand | Бренд |
| unit_cost | Себестоимость единицы |
| list_price | Базовая цена |

## sessions.csv

| Поле | Описание |
|---|---|
| session_id | ID сессии |
| customer_id | ID клиента |
| session_start | Дата и время начала сессии |
| channel | Маркетинговый канал сессии |
| device | Устройство |
| ab_group | Группа эксперимента |
| converted | 1 — в сессии создан заказ, 0 — нет |
| order_id | ID созданного заказа; пусто при converted=0 |

## orders.csv

| Поле | Описание |
|---|---|
| order_id | ID заказа |
| customer_id | ID клиента |
| order_date | Дата заказа |
| status | delivered / cancelled / returned |
| payment_method | Способ оплаты |
| shipping_type | Тип доставки |
| promo_code | Промокод |
| discount_percent | Скидка на заказ |
| gross_amount | Сумма до скидки |
| order_amount | Сумма после скидки |
| delivery_days | Срок доставки |
| customer_rating | Оценка клиента |

## order_items.csv

| Поле | Описание |
|---|---|
| item_id | ID строки заказа |
| order_id | ID заказа |
| product_id | ID товара |
| quantity | Количество |
| unit_price | Цена единицы в заказе до скидки на заказ |
| line_amount | quantity × unit_price |

## Связи

- customers.customer_id → orders.customer_id
- customers.customer_id → sessions.customer_id
- orders.order_id → order_items.order_id
- products.product_id → order_items.product_id
- sessions.order_id → orders.order_id для converted=1
