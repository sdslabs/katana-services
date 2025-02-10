# katana-services

Services to support the microservice architecture of Katana. There are three main componenets:
+ ## Kashira:
Its main purpose is to handle flag submissions and update scores.
Other than that it also handles execution of getter/setter scripts.

Getter scripts are used to fetch the flag for a particular challenge which can then be used
to check if it has been tampered

Setter scripts are used to update challenge flag at random intervals