#!/bin/bash

cd fantasy_simulator_lambda/tests

pytest --cov=../utils --cov-report=term-missing

cd ../..
