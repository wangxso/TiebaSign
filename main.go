package main

import (
	"io/ioutil"
	"log"

	"gopkg.in/yaml.v2"
)

type Config struct {
	BDUSS string `yaml:"BDUSS"`
}

var config Config

func init() {
	yamlFile, err := ioutil.ReadFile("./config.yaml")
	if err != nil {
		log.Println(err.Error())
	}
	yaml.Marshal(yamlFile)
}
