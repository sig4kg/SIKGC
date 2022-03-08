import torch
import pandas as pd

print("debug cudf.")
if torch.cuda.is_available():
    import cudf
    print("using cudf ...")
    pdf = pd.DataFrame({'a': [0, 1, 2, 3], 'b': [0.1, 0.2, None, 0.3]})
    gdf = cudf.DataFrame.from_pandas(pdf)
    print(gdf)
    pdf2 = gdf.head().to_pandas()
    print(pdf2)