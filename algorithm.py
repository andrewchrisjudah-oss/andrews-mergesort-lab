"""Stable Merge Sort with independent execution snapshots."""
from copy import deepcopy
import re


def parse_array(text):
    tokens = re.split(r"[\s,]+", text.strip())
    if not text.strip() or len(tokens) > 16 or any(
        not re.fullmatch(r"[-+]?\d+", t) or abs(int(t)) > 999 for t in tokens
    ):
        raise ValueError("Enter 1–16 integers between −999 and 999, separated by commas or spaces.")
    return [int(t) for t in tokens]


def simulate(values):
    if not values:
        raise ValueError("At least one element is required.")
    array = [(v, i) for i, v in enumerate(values)]
    nodes, events = [], []
    comparisons = writes = 0

    def emit(kind, message, node_id, **extra):
        events.append(deepcopy(dict(kind=kind, message=message, node_id=node_id,
            array=array, nodes=nodes, comparisons=comparisons, writes=writes, **extra)))

    def sort(lo, hi, depth, parent=None):
        nonlocal comparisons, writes
        node_id = len(nodes)
        node = dict(id=node_id, lo=lo, hi=hi, depth=depth, parent=parent,
                    items=array[lo:hi], state="pending")
        nodes.append(node)
        if parent is None:
            emit("initial", "Begin with the unsorted array.", node_id)
        if hi - lo == 1:
            node["state"] = "sorted"
            emit("base", "One element is already sorted: this is the base case.", node_id)
            return array[lo:hi]
        mid = lo + (hi - lo) // 2
        node["state"] = "split"
        emit("split", f"Split [{lo}, {hi}) at {mid}. Recursively sort the left half, then the right half.", node_id)
        left, right = sort(lo, mid, depth + 1, node_id), sort(mid, hi, depth + 1, node_id)
        i = j = 0
        buffer = []
        node["state"] = "merging"

        def merge_event(kind, message):
            emit(kind, message, node_id, left=left, right=right, i=i, j=j, buffer=buffer)

        merge_event("merge", "Both halves are sorted. Build a temporary sorted buffer.")
        while i < len(left) and j < len(right):
            comparisons += 1
            choose_left = left[i][0] <= right[j][0]
            merge_event("compare", f"Compare {left[i][0]} and {right[j][0]}. Choose {'left' if choose_left else 'right'}; ties choose left to preserve stability.")
            if choose_left:
                buffer.append(left[i]); i += 1
            else:
                buffer.append(right[j]); j += 1
            merge_event("take", f"Append {buffer[-1][0]} to the buffer.")
        while i < len(left) or j < len(right):
            if i < len(left):
                buffer.append(left[i]); i += 1
            else:
                buffer.append(right[j]); j += 1
            merge_event("remainder", f"Append remaining element {buffer[-1][0]} without a comparison.")
        array[lo:hi] = buffer
        writes += len(buffer)
        node.update(items=buffer[:], state="sorted")
        merge_event("merged", f"Copy the buffer into [{lo}, {hi}). This portion is sorted.")
        return buffer

    sort(0, len(array), 0)
    emit("done", "The entire array is sorted. Equal values retain their original order.", 0)
    return events
