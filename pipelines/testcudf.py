import torch
import  pandas as pd

if torch.cuda.is_available():
    try:
        import cudf
        print("using cudf ...")
        pdf = pd.DataFrame({'a': [0, 1, 2, 3], 'b': [0.1, 0.2, None, 0.3]})
        gdf = cudf.DataFrame.from_pandas(pdf)
        print(gdf)
        pdf2 = gdf.head().to_pandas()
        print(pdf2)
    except Exception as err:
        print("using pandas ...")
        print(err)