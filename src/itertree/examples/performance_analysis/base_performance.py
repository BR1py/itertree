import abc
import timeit

class BasePerformance(abc.ABC):

    def __init__(self,objects,trees,trees2,max_items,slice_operation_factor,width,repeat,itree_only,tmp_folder):
        self.objects=objects
        self.trees=trees
        self.trees2=trees2
        self.max_items=max_items
        self.slice_operation_factor=slice_operation_factor
        self.width=width
        self.repeat=repeat
        self.itree_only=itree_only
        self.tmp_folder=tmp_folder
        self.items_per_level=10

    def set_items_per_level(self,number):
        self.items_per_level=number

    def calc_timeit(self,check_method, *args):
        min_time = float('inf')
        for _ in range(self.repeat):
            t = timeit.timeit(lambda: check_method(*args), number=1)
            if t < min_time:
                min_time = t
        return min_time

    def print_time_meas_output(self,exec_time, content_s, compare_time_s=None, width=None,post_text=None):
        try:
            if not width:
                width=self.width

            if type(content_s) is list:
                for c in content_s[:-1]:
                    print(c)
                content_s = content_s[-1]
            spaces = width-len(content_s)
            if spaces < 0:
                spaces = 1
            if exec_time is None:
                if post_text is None:
                    post_text=' -> skipped too slow'
                print('{}{: ^{width}} '.format(content_s,
                                                              '',
                                                              exec_time,
                                                              width=spaces)+post_text)
                return
            if exec_time is Exception:
                if post_text is None:
                    post_text='-> skipped issue in execution'
                print('{}{: ^{width}} '.format(content_s,
                                                '',
                                                exec_time,
                                                width=spaces)+post_text)

                return
            if compare_time_s is None:
                if post_text is None:
                    print('{}{: ^{width}}{:.6f} s'.format(content_s,
                                                          '',
                                                          exec_time,
                                                          width=spaces))

                else:
                    print('{}{: ^{width}}{:.6f} s ->  '.format(content_s,
                                                          '',
                                                          exec_time,
                                                          width=spaces)+post_text)

            elif type(compare_time_s) is list:
                if post_text is None:
                    print('{}{: ^{width}}{:.6f} s  -> {:.3f}x ({:.3f}x) faster as iTree'.format(content_s,
                                                                                            '',
                                                                                            exec_time,
                                                                                            (compare_time_s[0] / exec_time),
                                                                                            (compare_time_s[1] / exec_time),
                                                                                            width=spaces))
                else:
                    post_text=post_text.format((compare_time_s[0] / exec_time),(compare_time_s[1] / exec_time))
                    print('{}{: ^{width}}{:.6f} s ->  '.format(content_s,
                                                      '',
                                                      exec_time,
                                                      width=spaces) + post_text)

            else:
                if post_text is None:
                    print('{}{: ^{width}}{:.6f} s  -> {:.3f}x faster as iTree'.format(content_s,
                                                                                  '',
                                                                                  exec_time,
                                                                                  (compare_time_s / exec_time),
                                                                                  width=spaces))
                else:
                    post_text=post_text.format((compare_time_s / exec_time))
                    print('{}{: ^{width}}{:.6f} s ->  '.format(content_s,
                                                      '',
                                                      exec_time,
                                                      width=spaces) + post_text)

        except:
            print('Issue in',exec_time, content_s, compare_time_s)
            raise

    @abc.abstractmethod
    def get_header(self):
        return ''

    @abc.abstractmethod
    def get_callers(self):
        return {}

    @abc.abstractmethod
    def test_exec(self):
        trees=self.trees
        trees2=self.trees2
        return trees,trees2

