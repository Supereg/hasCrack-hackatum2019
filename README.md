# ¿hasCrack?

¿hasCrack? is a project created at HackaTUM 2019 to solve the challenged pitched by the Allianz Deutschland AG.

##Requirements

The project needs the following components installed
* `node` and `npm`
* `python3` with the following dependencies:
    * `opencv-python`
    * `shapely`
    * `numpy`

##Installation

In order to setup the project you will first of all install all necessary npm modules,
which are required to run the web interface.
```
npm install
```

Install all the necessary python modules using `pip3 install <module>`.

##Run

To run the python script on it's own, navigate into the `src/analyzer` directory and run
the python script by supplying the following parameters.
```
python3 hull.py <inputFile> <outputFile>
```

To startup the http web interface you will need to transpile typescript to javascript initially
```
npm run build
```
and then startup up the http server:
```
npm run start
```

The http server will run on port `8080` by default. This can be changed by setting the `PORT` envoirment
variable. Additionally the `DEBUG` variable can be set to enable debug output.
