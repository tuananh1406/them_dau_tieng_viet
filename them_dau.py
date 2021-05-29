# coding: utf-8
'''Chương trình chuyển tiếng việt không dấu sang có dấu'''
import re
import pickle
import json
from tqdm import tqdm
import glob2


# https://realpython.com/python-encodings-guide/
# List các ký tự hợp lệ trong tiếng Việt
intab_l = "ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ"
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
digits = '0123456789'
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
whitespace = ' '
accept_strings = intab_l + ascii_lowercase + digits + punctuation + whitespace
r = re.compile('^[' + accept_strings + ']+$')


# Một câu sẽ được coi là hợp lệ nếu có các ký tự nằm trong accept_strings
def _check_tieng_viet(seq):
    if re.match(r, seq.lower()):
        return True
    else:
        return False


def save_train(path_train_dir, path_train_file):
    # Lưu file huấn luyện
    # tạo vòng lặp đi qua toàn bộ các file trong train folder. Kiểm tra câu có thỏa mãn tiêu chuẩn Tiếng Việt không,
    # đánh index cho câu và lưu đồng thời index và câu có dấu vào train file
    idx = 0
    for path in tqdm(glob2.glob(path_train_dir)):
        # Đọc nội dung của các văn bản từ folder output. Content sẽ chứa nhiều row, mỗi row là một json data
        with open(path, 'r', encoding='utf8') as f:
            content = f.readlines()
            for row in content:
                # Convert row sang json
                art_json = json.loads(row)
                # Lấy nội dung văn bản
                art_cont = art_json['text']
                art_cont = re.sub(r"(\s)+", r"\1", art_cont)
                # Chia văn bản thành các câu tại vị trí xuống dòng
                art_seqs = art_cont.split("\n")
                # Lưu các dòng là tiếng việt vào file 'train_tieng_viet.txt'.
                # Mỗi dòng có định dạng: index{10digits} sequence
                for seq in art_seqs:
                    if _check_tieng_viet(seq):
                        idx_str = str(idx).zfill(10)
                    with open(path_train_file, 'a') as f:
                        f.writelines([idx_str+'\t', seq+'\n'])
                    idx += 1


if __name__ == '__main__':
    is_vn = _check_tieng_viet('tiếng việt là ngôn ngữ của tôi')
    print(is_vn)
    save_train('output/*/*', 'train_tieng_viet.txt')
