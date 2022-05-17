# Kanaria toolbox for rarity ranking

## API test
We will use [Postman](https://www.postman.com/) to test endpoint. 
![image](https://user-images.githubusercontent.com/62699960/167423468-ea7cb04a-d4e0-4400-b919-526ce7ea9f06.png)
For this version of API public web URL generated with [SocetXP](https://www.socketxp.com/iot/how-to-access-python-flask-app-from-internet/) is `https://xivanxv2-hnrsd468js2xt6rq.socketxp.com/`.

It is worth to mention that our db in fact contains 2 modules: one for all data connected to kanbirds and another one with API users' data. Second module is required for authorization process and for now it is a preliminary version, which will be finalized in the future. 

Registration process within this version looks as following: user signs up and logs in to get authorization token (it has expiration date which also can be modified). With this token user gains access to other commands of 'users' module (such as modification of personal data and so on) and 'birds' module. All commands could be tested with Postman by changing blueprint and request method (POST, GET, etc). By blueprint we mean URL (1) + command part (2):

![image](https://user-images.githubusercontent.com/62699960/167427437-99f8cd40-b503-4c5e-a73b-8263dc736248.png)

All commands  will be described below as the combination of blueprint, request method and request body which should be used to reproduce the command.

### User module

#### Create user: POST + `api/v1/users/`
![image](https://user-images.githubusercontent.com/62699960/167428275-4f7c00cb-c924-4881-81e8-daed418e2371.png)

#### Login: POST + `api/v1/users/login`
![image](https://user-images.githubusercontent.com/62699960/167428911-467adbb6-ebc3-414f-ad43-4d3e43fabf10.png)
Returned token should be used as param in next requests which require authentication.

#### View own data: GET + `api/v1/users/me`, requires authentication
Provide token as `api-token` key value.
![image](https://user-images.githubusercontent.com/62699960/167430878-920ff76f-9a3f-4c6d-b8e9-26019f0b3c1b.png)

#### Edit own data: PUT + `api/v1/users/me`, requires authentication
![image](https://user-images.githubusercontent.com/62699960/167431217-0590b172-6a15-47c8-817c-f1a780d243b9.png)

#### Delete own data: DELETE + `api/v1/users/me`, requires authentication
![image](https://user-images.githubusercontent.com/62699960/167431538-ebeba6c3-4299-4b8b-a744-f0e223d1dd6b.png)

#### View all users: GET + `api/v1/users/`, requires authentication
![image](https://user-images.githubusercontent.com/62699960/167432231-2f21cb83-5bf9-4f29-a325-f14d94beb489.png)

### Kanbirds module

#### View all birds: GET + `api/v1/birds/`, requires authentication
![image](https://user-images.githubusercontent.com/62699960/167432983-47e1c6c5-4499-4fa0-af8c-b56f4d9d128f.png)

#### View bird by `id`: GET + `api/v1/birds/id`, requires authentication
![image](https://user-images.githubusercontent.com/62699960/167433257-7e62991e-59ce-45ff-9adc-dfee0d10175b.png)

