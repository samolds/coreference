# Coreference Resolution
A University of Utah Natural Language Processing project for
[CS 6340](http://www.eng.utah.edu/~cs5340/project.html).


## Dependencies
* Python2.7


## To Get Up and Running

```sh
git clone https://github.com/samolds/coreference.git
cd coreference
./setup.sh
```

NOTE: The first time you run `./run` after running `./setup` may take some
time because additional stuff will be downloaded. Many much helper NLTK data
will be installed at `$HOME/nltk_data`

NOTE: If you have a space (` `) in your path to this project, the setup script
is going to throw an error when trying to get virtualenv set up.


## Scripts

Then you can use this script to run the corefence response generator with
these two arguments:
`./run.sh <file with list of data files> <directory for responses>`

```sh
./run.sh data/filelists/devFiles.txt scorer/responses/
```

Then you can use this script to test the generated coreference responses
against the provided scorer with these two arguments:
`./test.sh <generated file with list of response files> <directory with data>`

```sh
./test.sh data/filelists/responselist.txt data/dev/
```


## Easy Testing

Runs entire program and then runs the corresponding tests with `data/dev/`
```sh
./complete.sh dev
```

Runs entire program and then runs the corresponding tests with `data/test1/`
```sh
./complete.sh test1
```


NOTE: The "complete.sh" script will also run setup.sh if you had not already.
So, technically, all you have to do to get this project running is clone, then
run `./complete.sh`.


## Authors
* [Carolina Nobre](https://github.com/cnobre)
* [Sam Olds](https://github.com/samolds)
