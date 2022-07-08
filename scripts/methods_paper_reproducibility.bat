cd ..
python main.py -b stanislaus -p -d -n "planning method" -s 1990 -e 1885
python main.py -b stanislaus -d -n "no planning method" -s 1995 -e 1995
python main.py -b stanislaus -n "no planning" -s 1990 -e 1995
python main.py -b stanislaus -p -n "planning" -s 1990 -e 1995
python main.py -b stanislaus -p -n "planning - no rr" -s 1990 -e 1995
python main.py -b upper_san_joaquin -n "no planning" -s 1980
python main.py -b upper_san_joaquin -p -n "planning" -s 1980
