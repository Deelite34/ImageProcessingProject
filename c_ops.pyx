def calc_cdf(image_list):
    cdf = {}
    image_list_sorted = sorted(image_list)
    for number in image_list:
        if number in cdf.keys():
            continue
        cdf[number] = count_smaller_nums(number, image_list_sorted)
    return cdf


def count_smaller_nums(number, inp_list):
    count = 0
    for i in inp_list:
        if i <= number:
            count += 1
        else:
            return count
    return count
