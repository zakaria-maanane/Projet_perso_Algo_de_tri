import time

class SortingAlgorithms:

    @staticmethod
    def selection_sort(arr, draw_swap=lambda *args: None):
        n = len(arr)
        for i in range(n):
            min_index = i
            for j in range(i + 1, n):
                if arr[j] < arr[min_index]:
                    min_index = j
            if i != min_index:
                draw_swap(arr, i, min_index)

    @staticmethod
    def bubble_sort(arr, draw_swap=lambda *args: None):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    draw_swap(arr, j, j + 1)

    @staticmethod
    def insertion_sort(arr, draw_swap=lambda *args: None):
        for i in range(1, len(arr)):
            j = i
            while j > 0 and arr[j] < arr[j - 1]:
                draw_swap(arr, j, j - 1)
                j -= 1

    @staticmethod
    def merge_sort(arr, draw_swap=lambda *args: None):
        def merge_sort_rec(start, end):
            if end - start > 1:
                mid = (start + end) // 2
                merge_sort_rec(start, mid)
                merge_sort_rec(mid, end)
                left = arr[start:mid]
                right = arr[mid:end]
                i = j = 0
                for k in range(start, end):
                    if i < len(left) and (j >= len(right) or left[i] < right[j]):
                        arr[k] = left[i]
                        i += 1
                    else:
                        arr[k] = right[j]
                        j += 1
                    draw_swap(arr, k, k)
        merge_sort_rec(0, len(arr))

    @staticmethod
    def quick_sort(arr, draw_swap=lambda *args: None):
        def quick_sort_rec(start, end):
            if start < end:
                pivot = arr[end]
                i = start
                for j in range(start, end):
                    if arr[j] <= pivot:
                        draw_swap(arr, i, j)
                        i += 1
                draw_swap(arr, i, end)
                quick_sort_rec(start, i - 1)
                quick_sort_rec(i + 1, end)
        quick_sort_rec(0, len(arr) - 1)

    @staticmethod
    def heap_sort(arr, draw_swap=lambda *args: None):
        def heapify(n, i):
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and arr[left] > arr[largest]:
                largest = left
            if right < n and arr[right] > arr[largest]:
                largest = right
            if largest != i:
                draw_swap(arr, i, largest)
                heapify(n, largest)
        n = len(arr)
        for i in range(n // 2 - 1, -1, -1):
            heapify(n, i)
        for i in range(n - 1, 0, -1):
            draw_swap(arr, 0, i)
            heapify(i, 0)

    @staticmethod
    def comb_sort(arr, draw_swap=lambda *args: None):
        n = len(arr)
        gap = n
        shrink = 1.3
        sorted = False
        while not sorted:
            gap = int(gap / shrink)
            if gap <= 1:
                gap = 1
                sorted = True
            i = 0
            while i + gap < n:
                if arr[i] > arr[i + gap]:
                    draw_swap(arr, i, i + gap)
                    sorted = False
                i += 1