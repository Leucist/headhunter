# HeadHunter

> v = 1.0  
> author: [leucist](https://github.com/Leucist/)  
> EPAM hackathon project  

## About >
HeadHunter is a python project made in order to help companies simplify the hiring process and avoid some extra face-to-face communication in the pandemic time.
The main aim of this bot is to conduct the first plain interview on the list of questions provided from the HR, who has the special-access rights and is identified by personal id. Then the aplication form with questions and interviewee's answers is being sent to the HR.

## Original Idea >
The project was implemented using the Telegram bot, which is filled with company's available vacancies and questions for a preliminary interview. Further, when searching for new employees, the company simply offers them to “get an interview” in the chatbot, answering a number of predefined questions. The application form formed as a result will be sent to the HR-department/personnel selection department of the company, where a decision will be made regarding the hiring an employee for a position or re-interview, etc. In order to bring the interview conditions closer to the real ones or to stimulate their honesty, you can limit the time available to the applicant to answer the question. This way, instead of paying for the working hours of the employee who conducts interviews on the established list of questions, the company can simply allocate funds once to buy a bot that automates this process and compensates for the money spent. This saves company funds, time and labor costs.

## HR's functionality >
After writing "/admin" command to the bot user riches the access to control the bot only if his id matches the one in code.
If nothing interferes, admin is able to change vacancy-list¹, blacklist², check databases and send the mailing to the all users or to one user personally.
> 1) This way Admin is able to add new vacancies to the list, remove extra-ones or see the whole list.
> 2) This way Admin is able to add new users to the blacklist, remove extra-ones or see the whole list.

## Interviewee functionality >
Interviewee is able to look through the list of vacancies available in all branches of the company and fill the application form by answering questions for the chosen vacancy.
If HRs find it acceptable interviewee will get a respond.
