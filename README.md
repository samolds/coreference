# Coreference Resolution
A University of Utah Natural Language Processing project for
[CS 6340](http://www.eng.utah.edu/~cs5340/project.html)


## Dependencies
* Python2.7
* Pip


## To Get Up and Running

```sh
git clone https://github.com/samolds/coreference.git
cd coreference
./setup.sh
```

Then you can use this to run it whenever

```sh
./run.sh
```

NOTE: The first time you run this after running `./setup`, it may take some
time because additional stuff will be downloaded. Many much helper NLTK data
will be installed at `$HOME/nltk_data`


## To Test

Runs entire program and then runs the corresponding tests against dev data
```sh
./testdev.sh
```

Runs entire program and then runs the corresponding tests against test1 data
```sh
./test1.sh
```


## Authors
* [Carolina Nobre](https://github.com/cnobre)
* [Sam Olds](https://github.com/samolds)
