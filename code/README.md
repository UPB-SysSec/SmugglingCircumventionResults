## Instructions

  

### Requirements
* python > 3.7
* a control server
* a server that is suspected to be subject to censorship as a vantage point.

## Instructions
### 1 - Control server
The control server acts as a ground truth, to which we send http requests and know what the response should be.
On the control server, configure  the multiport server:
- In `multiport_server.py` configure the ports (line 6+7)
	- For censors with possible residual censorship on ports, use multiple ports, otherwise its possible to use port 80 only.
- Run multiport server with `$ python multiport_server.py`.

### 2 - Vantage Point
The vantage point is a machine for which we expect some http requests to be censored.
#### 2.1 Set up enviromnent
```
$ git clone https://github.com/UPB-SysSec/SmugglingCircumventionResults.git
$ cd SmugglingCircumventionResults
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```
#### 2.2 Configure and run scan

* In shrec_paper.py set the following constants:

	* PORTS: Same as configured for the control server

	* STARTPORT: Same as configured for the control server

	* DST_HOST: IP address of the control server

* Configure domain lists
	* Find uncensored and censored hosts for the vantage point
	*  Add these hosts to two .csv files in `data/urls/` named `{$countrycode}_censored.csv` and `{$countrycode}_uncensored.csv`, respectively.

* Run evasion scan: `python shrec_paper.py` with the following arguments:
	* `-c` country code used for the domain lists (e.g. `-c cn`).
	* `-t` amount of threads to use for the evasion scan.
	* `--timeout` sets socket timeout.
	* `--residual-timer`time to wait before reusing a socket, if scanning on multiple ports.

* The request smuggling vectors are stored encoded in `data/viable_vectors.csv`
