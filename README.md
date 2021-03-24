# ECL-CKH-Pig-Scale

## Requirements
- python3 version: 3.9.1
- Create a virtual environment and activate it
    ```
    # get to the directory of this repository
    $ cd <repository_name>
    # create a virtual environment
    $ python3 -m venv <env_name>
    # activate the virtual environment
    $ source <env_name>/bin/activate
    ```
- Install required package
    ```
    $ pip3 install -r requirements.txt
    ```

## Run the code
```
$ python3 main.py
```

## Reference
- Here is the [Document](Docs/Document.md) you may have to read to know the structure of the program.


## Repo Structure
```
.
├── README.md
├── requirements.txt
├── main.py
├── Structure
│   ├── DataStructure.py
│   └── SerialThread.py
├── Utils
│   ├── analyze,py
│   ├── hovertip.py
│   ├── Logger.py
│   └── Utils.py
├── Views
│   ├── GUI.py
│   ├── StartView.py
│   ├── ScaleView.py
│   └── AnalyzeView.py
├── Docs
│   ├── 1202fence1.log
│   ├── AnalyzeDataManual.md
│   ├── Document.md
│   └── Pig_Scale_report2.0.pdf
└── .gitignore
```
