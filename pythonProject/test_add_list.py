# test_add_list.py
from add_list import Add_list

def test_add_list_basic():
    self_data = [['s+', 90001], ['a', 90002]]
    pangle_data = [['s', 10004], ['a', 10005]]
    top_data = [90001]

    adder = Add_list(self_data, pangle_data, top_data)
    final = adder.build_final_list()

    assert len(final) == 4
    # 置顶的 90001 应该在前面
    assert final[0][1] == 90001

if __name__ == "__main__":
    test_add_list_basic()
    print("✅ 测试通过")