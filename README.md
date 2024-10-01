# MODERATE QUALITY CHECK REPORT TOOL

## Description

This tool allows users to upload an EPC (Energy Performance Certificate) in its standard XML format. The system then analyzes the file and identifies any inconsistencies or discrepancies found based on predefined rules.

The frontend, located in `src/front/`, handles all UI/UX-related functionality. This includes sending the XML document to the backend via a RESTful API and receiving the corresponding response.

![Modules diagram](img/modules-diagram.png)

To run the application, a Taskfile is used. This is an alternative to Makefile, written in YAML syntax. The defined tasks are "start," "stop," "build," and "logs." To execute these tasks, you can run the following command:

```sh
task build start logs
```

This will build the Docker image, run the system in the background using the docker-compose.yaml file, and finally display the logs in the console.

## EPC examples

The `epcs/` folder contains some anonymized examples. These can be used for development and testing purpouses.

## Back

The backend defines a set of REST endpoints to facilitate remote communication.
Currently, the implemented endpoint is located at the URI `/upload` and accepts only POST requests. The file to be analyzed should be included in the body of the request.

## Front

The frontend is currently a basic HTML page that makes a request to the /upload endpoint. It parses the file and returns the necessary HTML to display the content on the web page, which is then embedded directly after the response is received.

## Future developments

### Cadastre API Integration

In the future, the tool is intended to integrate with the Cadastre API to make HTTP GET requests to the following URI:

```
http://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCallejero.svc/json/Consulta_DNPRC?RefCat=5223603YJ2752C0006UD`
```

In the `cadaster/` folder, you can find an example XML response from the API, along with an XML file containing the field names and the XSD schema that defines the XML structure.
