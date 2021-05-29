# coding: utf-8
'''Chương trình chuyển tiếng việt không dấu sang có dấu'''
import re
import pickle
import json
from tqdm import tqdm
import glob2


def _check_tieng_viet(seq):
    '''Một câu sẽ được coi là hợp lệ nếu có các ký tự nằm trong accept_strings'''

    # https://realpython.com/python-encodings-guide/
    # List các ký tự hợp lệ trong tiếng Việt
    intab_l = "ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ"
    ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    digits = '0123456789'
    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    whitespace = ' '
    accept_strings = intab_l + ascii_lowercase + digits + punctuation + whitespace
    result = re.compile('^[' + accept_strings + ']+$')
    return bool(re.match(result, seq.lower()))


def _save_pickle(filename, obj):
    '''Lưu dữ liệu để tái sử dụng sau này'''
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)


def save_train(path_train_dir, path_train_file):
    '''Lưu file huấn luyện
    tạo vòng lặp đi qua toàn bộ các file trong train folder. Kiểm tra câu có thỏa mãn tiêu chuẩn Tiếng Việt không,
    đánh index cho câu và lưu đồng thời index và câu có dấu vào train file
    '''
    idx = 0
    for path in tqdm(glob2.glob(path_train_dir)):
        # Đọc nội dung của các văn bản từ folder output. Content sẽ chứa nhiều row, mỗi row là một json data
        with open(path, 'r', encoding='utf8') as raw_data:
            content = raw_data.readlines()
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
                    with open(path_train_file, 'a') as train_file:
                        train_file.writelines([idx_str+'\t', seq+'\n'])
                    idx += 1


def remove_tone_line(input_string):
    '''Hàm xoá dấu, chuyển tiếng việt có dấu sang không dấu'''

    intab_l = "ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ"
    intab_u = "ẠẢÃÀÁÂẬẦẤẨẪĂẮẰẶẲẴÓÒỌÕỎÔỘỔỖỒỐƠỜỚỢỞỠÉÈẺẸẼÊẾỀỆỂỄÚÙỤỦŨƯỰỮỬỪỨÍÌỊỈĨÝỲỶỴỸĐ"
    intab = list(intab_l+intab_u)

    outtab_l = "a"*17 + "o"*17 + "e"*11 + "u"*11 + "i"*5 + "y"*5 + "d"
    outtab_u = "A"*17 + "O"*17 + "E"*11 + "U"*11 + "I"*5 + "Y"*5 + "D"
    outtab = outtab_l + outtab_u
    # Khởi tạo regex tìm kiếm các vị trí nguyên âm có dấu 'ạ|ả|ã|...'
    result = re.compile("|".join(intab))

    # Dictionary có key-value là từ có dấu-từ không dấu. VD: {'â' : 'a'}
    replaces_dict = dict(zip(intab, outtab))
    # Thay thế các từ có dấu xuất hiện trong tìm kiếm của regex bằng từ không dấu tương ứng
    non_dia_str = result.sub(lambda m: replaces_dict[m.group(0)], input_string)
    return non_dia_str


def split_train_val_test(path_train_file):
    '''Chia dữ liệu thành các tập train, val, test'''
    train_idx_500k = []
    train_opt_500k = []
    train_ipt_500k = []
    val_idx_50k = []
    val_opt_50k = []
    val_ipt_50k = []
    test_idx_50k = []
    test_opt_50k = []
    test_ipt_50k = []

    for i in tqdm(range(600000)):
        [idx, origin_seq] = path_train_file[i].split('\t')
        try:
            non_acc_seq = remove_tone_line(origin_seq)
        except Exception as error:
            print('error remove tone line at sequence {}', str(i))
            print(error)
            continue
        if i < 500000:
            train_idx_500k.append(idx)
            train_opt_500k.append(origin_seq)
            train_ipt_500k.append(non_acc_seq)
        elif i < 550000:
            val_idx_50k.append(idx)
            val_opt_50k.append(origin_seq)
            val_ipt_50k.append(non_acc_seq)
        else:
            test_idx_50k.append(idx)
            test_opt_50k.append(origin_seq)
            test_ipt_50k.append(non_acc_seq)
    _save_pickle('train_tv_idx_500k.pkl', train_idx_500k)
    _save_pickle('val_tv_idx_50k.pkl', val_idx_50k)
    _save_pickle('test_tv_idx_50k.pkl', test_idx_50k)


if __name__ == '__main__':
    is_vn = _check_tieng_viet('tiếng việt là ngôn ngữ của tôi')
    print(is_vn)
    khong_dau = remove_tone_line('Đi một ngày đàng học 1 sàng khôn')
    print(khong_dau)
    # path_train_dir = 'output/*/*'
    # path_train_file = 'train_tieng_viet.txt'
    # save_train(path_train_dir, path_train_file)
    # split_train_val_test(path_train_file)
