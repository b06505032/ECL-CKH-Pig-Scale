# ECL-CKH-Pig-Scale

## Requirements
- python3 version: 3.9.1
- Create a virtual environment and activate it
    ```
    $ cd <repository_name>
    $ python3 -m venv <env_name>
    $ source <env_name>/bin/activate
    ```
- Install required package
    ```
    pip3 install -r requirements.txt
    ```

## Run the code
```
$ python3 main.py
```

## Reference
- The [Document](https://hackmd.io/@gcAQO6FETE6ZHMRzgzc67A/S1PPtG6MO) you may have to read


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
└── .gitignore
```