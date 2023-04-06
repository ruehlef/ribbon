# Find ribbon bands
The python package ribbon provides code that searches for ribbon bands in knots or links. Below is an example for the first ribbon knot, the Stevedore knot.
![Ribbon plots](/assets/stevedore.png)


## Features
- Randomly tries to attach bands and simplify the resulting link until the unknot is reached, which proves that the link is ribbon
- The resulting band is (admittedly very poorly) visualized and saved to a file.
- We provide many options for customizing the search

## Installation
This guide assumes that you have a working Python 3 (version 3.8, 3.9, or 3.10) installation (and optionally Sage, if you want to use some features from snappy that require sage). It is assumed that running ```python3``` or ```sage``` works on your system and runs python 3.8 or above.  Moreover, it is assumed that you have installed git. Note that both are standard on Mac and most Linux distributions. 

*NOTE*: At the moment, the code is still closed source, which means that it ships with a Cython binary. I have compiled one version for Python 3.8-3.10 with a Macbook with an M1 chip and one with Ubuntu 22.04LTS. 

We describe the installation progress at two levels:
A: I can't be bothered: Use that if you just want to try the code on some knot (given in terms of a PD code) and you are not familiar/ comfortable with using the terminal

B: Standard: Use this if you want to know a bit more background on what the code can do and what you are actually installing

### A: I can't be bothered
1. You will need to open a terminal. On Mac, press command and space simultaneously, type terminal, and hit enter. On Linux, press Ctrl + Alt + T.
2.a. If you want to use python, enter ```python3 --version``` and press enter. If the output is not ```Python 3.8``` or similar, ask someone to install python 3.8 for you. 
2.b. If you want to use sage, type ```sage -v```. If the output is not  ```SageMath 9.5``` or similar, ask someone to install sage.
3.a. If you want to use python, copy the line below and press enter
```console
pip install --user git+https://github.com/ribbon/ribbon.git
```
3.b. If you want to use sage, you need to start it first by typing ```sage``` and pressing enter. Next copy the line 
```console
pip install --user git+https://github.com/ribbon/ribbon.git
```
and press enter. Once this is done, type ```exit``` and press enter
4. Download [this file](/examples/test_ribbon.py).
5.a. If you want to use python, run 
```console
python test_ribbon.py --links 'K6a3' --save-images --max-tries -1 
```
Wait until it finds a band (it will telly you and stop), or just close the terminal window when you want to stop. You should replace 'K6a3' by the name of the knot you want to try, or by its PD code, so e.g.
```console
python test_ribbon.py --links '[[2, 0, 3, 11], [0, 7, 1, 8], [6, 1, 7, 2], [10, 4, 11, 3], [4, 10, 5, 9], [8, 6, 9, 5]]' --save-images --max-tries -1 
```
5.b. If you want to use python, run 
```console
sage test_ribbon.py --links 'K6a3' --save-images --max-tries -1 
```
Wait until it finds a band (it will telly you and stop), or just close the terminal window when you want to stop. You should replace 'K6a3' by the name of the knot you want to try, or by its PD code, so e.g.
```console
python test_ribbon.py --links '[[2, 0, 3, 11], [0, 7, 1, 8], [6, 1, 7, 2], [10, 4, 11, 3], [4, 10, 5, 9], [8, 6, 9, 5]]' --save-images --max-tries -1 
```

### B: Standard
Create a new virtual environment in a terminal with

```console
python3 -m venv ~/venv-ribbon
```

Then install with pip directly from github 
```console
source ~/venv-ribbon/bin/activate
pip install --upgrade pip
pip install git+https://github.com/ribbon/ribbon.git
```

If you want to use the jupyter notebook, you need to install it and add the virtual environment as a kernel
```console
pip install jupyter notebook
python -m ipykernel install --user --name=ribbon-venv
```

Since Sage comes with python,  you can easily install the code for sage. All you need to do is run 
```console
pip install git+https://github.com/ribbon/ribbon.git
```
from within sage (either the command line interface or in a notebook).

## Examples

We provide two examples for how to use the code. One is a command line tool, and one is a (Python) notebook.

### Command line
Once you have installed the package (either in python or sage), you are ready to use the code. The file [test_ribbon.py](/examples/test_ribbon.py) provides basic functionality for that. To see the different options available and some examples, download the file and run it with 
```python test_ribbon.py --help```

If you have Sage installed and followed the steps to install it for usage with Sage outlined above, you could run instead
```sage test_ribbon.py --help```
Sage is only needed if you run the code with the ```--use-checks``` options, which checks the Fox-Milnor condition, which requires computing the Alexander polynomial in snappy, which in turn requires sage.

### Python notebook
If you prefer to work with a ipython notebook (either within python or sage), you can look at [test_ribbon.ipynb](/examples/ribbon_example.ipynb)

## Output 
Besides the text / logging output, the code can visualize the band. The algorithm works by operating on the dual graph, hence the band description is given in terms of the dual graph as well. An example output is shown in [knot plot](/assets/stevedore.png). The output will always be of the form with s# a# ... a#. Here is a short explanation for how to read the output:

* s# a#: indicates that the band is started on the strand that is crossed when going from the region indicated by the number that follows s to the region indicated by the number that follows a (these are acropnyms for "start" and "attach")
* o#:    Indicates that the band is moved from the current region into the next region by crossing over the strand that is encountered
* u#:    Indicates that the band is moved from the current region into the next region by crossing over the strand that is encountered
* t+-:   Indicates that the band is twisted (either a positive or a negative twist)
* a#:    Indicates that the band is attached at the strand that is crossed when leaving the current region and entering the region indicated by the number following a

For the [example knot](/assets/stevedore.png) shown at the top of the page, this means that a band is started at the horizontal strand between regions 1 and 2, moves through region 2 where a positive twist is inserted, and then gets attached at the strand in the middle of the knot that separates regions 2 and 6.

## Advanced: Working directly with the compiled code
The main class is the RandomWalker class. At the moment, it is closed source, but we will open source it soon. It takes the following arguments:
```
Args:
    links (list)                   : list of links to check whether they are ribbon
    max_size (int)                 : maximum number of crossings
    max_steps (int)                : maximum number of steps. Roughly, each crossed arc corresponds to one step.
    max_bct (int)                  : max number of twists, or components, or number of bands that we allow before for a knot (note that bands and components are correlated if the starting object is a knot)
    logger (logging.logger)        : logger to print info. If None, a logger will be created
    use_band_checks (bool)         : Set to True to check some known obstructions to sliceness after adding a band. Note this can be slower than omitting this step for large knots since some knot invariants (like the Alexander Polynomial) are quite computationally expensive.
    save_solved_knot_images (bool) : Set to True to save images that illustrate the bands (for verification).
Returns:
    A new RandomWalker class instance
```
From this class, you essentially only need the ```invalid_action_mask()``` and ```step(action)``` methods. The former returns a list, which contains a 1 for actions that are valid in the current state and a 0 for actions that are invalid. You can then choose randomly (or in an informed way, if you know which band you want to construct) an action and perform it using the ```step``` method. The step function will return a bool indicating whether it is resetting the knot. The reason for the reset is given in the second argument.
