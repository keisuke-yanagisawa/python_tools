python reorder_sdf_by_list.py -i testfiles/test.sdf -o temp.sdf -l testfiles/test.list \
    && echo NG || echo OK
python reorder_sdf_by_list.py -i testfiles/test.sdf -o temp.sdf -l testfiles/test.list --ignore-notfound \
    && echo OK || echo NG

