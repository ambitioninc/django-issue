#!/bin/bash

# In my setup, these are all set by direnv via the project .envrc file
: ${PROJTAG:=djissue}
: ${PGDATA:=../pgdata/${PROJTAG}}
: ${PYTAG:=37}
: ${PROJ_VENV:=../venv/${PROJTAG}_${PYTAG}}

export PGDATABASE=postgres
PIP=${PROJ_VENV}/bin/pip    

function init_venv() {
    if [[ $1 == "force" ]]; then rm -rf $PROJ_VENV; fi
    if [[ ! -d $PROJ_VENV ]]; then
	echo "Virtual environment not found; initializing..."
	$PROJ_PY -m venv $PROJ_VENV
	$PIP install -U pip wheel setuptools
    fi
}

function init_pgdata() {
    if [[ $1 == "force" ]]; then rm -rf $PGDATA; fi
    if [[ ! -s ${PGDATA}/PG_VERSION ]]; then
	echo "Database not found; initializing..."
	initdb --username=$PGDATABASE --pwfile=<(echo $PGDATABASE) -D $PGDATA
    fi
}

function install_requirements() {
    $PIP install -r requirements/requirements.txt
    $PIP install -r requirements/requirements-testing.txt
}


if [[ $DOCKER == 1 ]]; then
    DBHOST=db
else
    DBHOST=localhost
fi

export DB_SETTINGS='{"ENGINE":"django.db.backends.postgresql","NAME":"dynamic_initial_data","USER":"postgres","HOST":"'$DBHOST'"}'


function test_flake() {
    $PROJ_VENV/bin/flake8 .
}

function test_django() {
    version=$1
    if [[ $version == 2 ]]; then version="<3"
    elif [[ $version == 3 ]]; then version="<4"
    elif [[ $version == 4 ]]; then version="<5"
    fi
    	
    pg_ctl -D $PGDATA -l /dev/null start
    $PIP install -U "Django$version"
    python manage.py check
    python run_tests.py --verbosity 2
    pg_ctl stop
}

function init_all() {
    init_venv
    init_pgdata
    install_requirements
}

function test_all() {
    test_django 2
    test_django 3
    test_django "<4.1"
    test_django "<4.2"
}

function do_all() {
    init_all
    test_all
}

_main() {
    cmd=$1
    if [[ $cmd == init ]]; then
	init_all
    elif [[ $cmd == test ]]; then
	test_all
    elif [[ $cmd == all ]]; then
	do_all
#    elif $cmd is a function that exists, just run that and pass params
    else
	cat <<-EOF
test_local.sh < init | test | all >
Test this project locally. Dot-include instead to run functions more granularly. Functions include:
init_venv [ force ]
init_pgdata [ force ]
install_requirements
test_django < 2 | 3 | 4 | [ pip qualifier like ==3.1.1 ]
init_all
test_all
EOF
    fi
    
    source ${PROJ_VENV}/bin/activate
}

# check to see if this file is being run or sourced from another script
_is_sourced() {
    # https://unix.stackexchange.com/a/215279
    [ "${#FUNCNAME[@]}" -ge 2 ] \
	&& [ "${FUNCNAME[0]}" = '_is_sourced' ] \
	&& [ "${FUNCNAME[1]}" = 'source' ]
}

if ! _is_sourced; then
    _main "$@"
else
    echo "Test environment for [ $PROJNAME ] initialized!"
fi
