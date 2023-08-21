# heliolinc-investigation

## Contributors

- Jeffrey Lan: third-year UW astronomy undergrad, [blan2@uw.edu](mailto:blan2@uw.edu)
- Jake Kurlander: first-year UW astronomy grad student, [jkurla@uw.edu](mailto:jkurla@uw.edu)
- Ari Heinze: Research scientist, HelioLinC implementer, [ariheinze@hotmail.com](mailto:ariheinze@hotmail.com)

## Related Projects

- https://github.com/kjnapier/spacerocks
- https://github.com/lsst-dm/heliolinc2

## Set Up

### Set up HelioLinc

Download HelioLinc:

```jsx
git clone https://github.com/lsst-dm/heliolinc2
```

Build & compile HelioLinc:

```bash
cd src
make -j4
```

- In MacOS, follow the following steps
  - Download the real gcc (by default command `g++` in MacOS still points to `clang` , which will results in `clang: error: unsupported option '-fopenmp'`
    ```bash
    brew install gcc
    ```
  - Find the gcc version:
    ```bash
    ls /usr/local/bin/g++*
    ```
  - Add the following line to the top of the Makefile under `src`:
    - If the gcc version is `g++-13`
    ```bash
    CXX = g++-13
    ```

Test HelioLinc

Here’s a minimalist running of the `make_tracklets` command:

```bash
cd ./tests
../src/make_tracklets -dets LSST_raw_input_data01a.csv -earth Earth1day2020s_02a.txt \
 -obscode ObsCodes.txt -colformat colformat_LSST_01.txt
```

There should be two output file:

- `pairdetfile01.csv` is the **paired detection file**, which is just a reformatted version of the input detection catalog limited only to detections that formed pairs or longer tracklets.
- `outpairfile01` is the **pair file**, which records the pairs and longer tracklets that were found using integer indices that specify their position in the paired detection file.

For more on testing, see [HelioLinc2 Documentation](https://github.com/lsst-dm/heliolinc2#testing-make_tracklets).

### Set Up `spacerocks`

Running `pip install spacerocks` usually failed. Instead, try building the package from source.

```bash
git clone https://github.com/kjnapier/spacerocks
cd spacerocks
python setup.py build_ext -i
pip install .
```

- On MacOS, you need to install two packages using `brew` **************\*\***************\*\*\*\***************\*\***************before running `python [setup.py](http://setup.py) build_ext -i`\*\* :
  ```bash
  brew install libomp
  brew install swig
  ```
  Then, run `python [setup.py](http://setup.py) build_ext -i`
  If you run into error `ld: library not found for -lomp` , try to open `[setup.py](http://setup.py)` , at line 21, change
  ```bash
  extra_link_args = ['-Wl,-lomp,-install_name,@rpath/libspacerocks' + suffix]
  ```
  to
  ```bash
  extra_link_args = ['-L/usr/local/opt/libomp/lib -Wl,-lomp,-install_name,@rpath/libspacerocks' + suffix]
  ```
  by adding `-L/usr/local/opt/libomp/lib` flag
