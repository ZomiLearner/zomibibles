import re

##########################################################
def strip_outer(s):
    return s[1:-1] if s.startswith("(") and s.endswith(")") else s

##########################################################

import os
from huggingface_hub import HfApi

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN environment variable is not set")

def get_current_file_as_df():
    import pandas as pd
    return pd.read_csv(os.getenv("TBS_SMT_URL"))

def get_current_index():
    current_df = get_current_file_as_df()
    return current_df.shape[0]

def upload_hf_dataset_file(
    repo_id: str,
    path_in_repo: str,
    local_path: str,
    commit_message: str = "Upload file",
) -> str:
    """
    Upload a local file to a Hugging Face dataset repo.

    Args:
        repo_id: e.g. "username/my-dataset"
        path_in_repo: destination path inside the repo, e.g. "data/train.csv"
        local_path: path to the file on disk
        commit_message: commit message for the upload

    Returns:
        The URL of the commit on Hugging Face.
    """
    token = os.environ["HF_TOKEN"]  # fails fast if missing
    api = HfApi(token=token)

    return api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        repo_type="dataset",
        commit_message=commit_message,
    )

import os
import io
import pandas as pd
from huggingface_hub import HfApi

def upload_dataframe_to_hf_dataset(
    repo_id: str,
    path_in_repo: str,
    df: pd.DataFrame,
    commit_message: str = "Upload dataframe",
) -> str:
    token = os.environ["HF_TOKEN"]
    api = HfApi(token=token)

    # Write to an in-memory CSV buffer (nothing touches disk)
    buf = df.to_csv(index=False).encode("utf-8")

    return api.upload_file(
        path_or_fileobj=io.BytesIO(buf),
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        repo_type="dataset",
        commit_message=commit_message,
    )
  
def get_appended_df(new_data):
    import pandas as pd

    # Read existing data
    current_df = get_current_file_as_df()
    print(current_df.shape)
    
    # Create new DataFrame
    df = pd.DataFrame(new_data, columns=["b", "c", "v", "bcv", "verse_text", "verse_ref"])
    print(df.shape)
    
    # Append new data to existing data
    appended_df = pd.concat([current_df, df], ignore_index=True).drop_duplicates(subset=["bcv"])

    return appended_df

  
smt_bible = []
current_index = get_current_index()
for index, bcv in enumerate(verses):
  if index < current_index: 
    continue
  print(index)
  logger.info(f"Index: {index}")
  b, c, v = bcv.split("_")
  verse = fetch_tbs_verse("smt", b, c, v)
  # print(verse)
  verse_text, verse_ref = verse[0], verse[1]
  cv_ref = re.sub(r'^\((.*)\)$', r'\1', verse_ref)
  # print(cv_ref)
  cv_ref_split = cv_ref.split(" ")[1].split(":")
  # cv_ref_split = cv_ref_split[1].split(":")
  if c == cv_ref_split[0] and v == cv_ref_split[1]:
      smt_bible.append([b, c, v, bcv, verse_text, verse_ref])
  else:
      smt_bible.append([b, c, v, bcv, "No text available", "No text available"])
      print("Mismatch:", bcv, "->", verse_ref)

  if index % 100 == 0:
      previous_length = get_current_index()
      df_to_upload = get_appended_df(smt_bible)
      path_in_repo = f"tbs_smt.csv"
      repo_id = os.environ["USERNAME"] + "/" + os.environ["DATASET_REPO_NAME"]
      commit_message = f"Added {df_to_upload.shape[0]-previous_length} rows: {previous_length} to {df_to_upload.shape[0] - 1}" 
      logger.info(f"{commit_message}")
      upload_dataframe_to_hf_dataset(
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        df=df_to_upload,
        commit_message=commit_message,
      )

      # Reset the variables
      smt_bible = []
      current_index = get_current_index()
  
