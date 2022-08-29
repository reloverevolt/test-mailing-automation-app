# Example Web Service For Managing Mailing Campaigns

## Project Description:

The service's main goals are: 
* Provide API for Mailing Campaign creation and editing
* Provide API for Client adding and editing
* Automate sending mails under the Mailing Campaigns throughout the client list based on specified campaign settings
such as tag, mobile operator, time for sending the message
* Provide statistics on each mailing campaign progress

**Full API documentation will be available upon service build at /v1/docs/**  

## Setup and run the service:

### Add config
    Inside the project's root folder:
   * Create config.yaml (see reference in example.config.yaml)
   * Create .env (see reference in example.env)

### Run service
*Run ```make build``` to start up the docker compose infrastructure*
P.S. run ```make help``` to see all useful make commands for communicating with the service


### Дополнительный функционал из тестового задания:

* 1.Тестирование написанного кода. Частично. Тестируется 4 кейса на создание сущности Клиент
* 3.Подготовить docker-compose для запуска всех сервисов проекта одной командой
* 5.Cделать так, чтобы по адресу /docs/ открывалась страница со Swagger UI и в нём отображалось описание разработанного API
* 6.Pеализовать дополнительный сервис, который раз в сутки отправляет статистику по обработанным рассылкам на email.
Список получателей отчета может быть добавлен в файле config.yaml
* 7.Реализованы очереди позволяющие обрабатывать сообщения по сценариям:
    Сущность Message (Сообщение) имеет статусы:
    * ENQUEUED - Сообщение создано и ждет очереди на отправку
    * FAILED - Ошибка на стороннем сервере при попытке отправки сообщения
    * DELAYED - Сообщение отложено по причине часового пояса клиента 
    * EXPIRED - Сообщение не будет отправлено так как рассылка закончилась
    * SUCCESS - Собщение успешно отправлено
* 11.В модели Рассылка (Mailing Campaign) были добавлены
дополнительные параметры: ```allowed_from_time``` и ```allowed_to_time```,
а так же в модели Клиент (Client) параметр ```timezone``` со свойством time_now, что позволяет дополнительно
проверять соответствует ли настояшее время в часом поясе клиента благоприятному времени отправки сообщения,
заданному в параметрах Рассылки. Дополнительно была автоматизированна загрузка словаря часовых поясов в базу данных
при каждой сборке приложения
* 12.Логи основных событий записываются в файл app.log и могут быть отфильтрованы 
по id сущностей через ```cat app.log | grep "message_id: {id}"```