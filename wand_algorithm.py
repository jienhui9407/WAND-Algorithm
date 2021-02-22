def first_posting(data):
    """returns the first posting from term
    :param data:
    :return: return the weight
    """
    try:
        return data[0][1]
    except:
        return float('inf')


def next_posting(data):
    """
    Advances the iterator for term t, and returns the next posting.
    :param data: the data which need to iterate
    :return: if data is out of range return a tumple(float('inf'), 0), otherwise return the next
    """
    try:
        return next(data)
    except:
        return (float('inf'), 0)


def seek_to_document(data, c_pivot):
    """
    Advances the iterator for term t to the first document number greater
    than or equal to c_pivot, and returns that posting.
    :param data:
    :param c_pivot:
    :return:
    """
    while True:
        try:
            (DID, weight) = next(data)
            if DID >= c_pivot:
                return (DID, weight)
        except:
            return (float('inf'), 0)


def WAND_Algo(query_terms, top_k, inverted_index):
    """
    We build a WAND funtion to get the topk result. A query q of
    |q| terms is to be processed using an index I which contains a
    postings list It for each term t that appears in the collection.
    :param query_terms: the words we need to search
    :param top_k: A total of k best results
    :param inverted_index:
    :return: topk_result and full evaluation count
    """
    UBlist = []  # upbound list: top weight each terms
    tmp_candidate = []  # temperature candidate
    candidates = {}  # iterator
    threshold = -1  # the most important value in WAND
    Ans = []  # topk results
    full_evaluation_count = 0  # times of full evluvate
    # from the for, we get temperature candidate, iterator of candidates and upboundlist.
    pos = 0
    for i in query_terms:
        term_data = inverted_index[i]
        candidates[pos] = iter(term_data)
        tmp_candidate.append((pos, next_posting(candidates[pos])))
        _term_data = sorted(term_data, key=lambda x: x[1], reverse=True)
        ub = first_posting(_term_data)
        UBlist.append((pos, ub))
        pos = pos + 1

    # WAND circular logic, find topk, iterate the terms
    correct = True
    while correct:
        score_limit = 0
        pivot = 0
        tmp_candidate.sort(key=lambda x: x[1][0])
        while pivot < len(query_terms) - 1:
            DID = tmp_candidate[pivot][0]
            for i in UBlist:
                if i[0] == DID:
                    ub_weight = i[1]
            tmp_s_lim = score_limit + ub_weight
            if tmp_s_lim > threshold:
                break
            score_limit = tmp_s_lim
            pivot = pivot + 1

        c_pivot = tmp_candidate[pivot][1][0]
        if tmp_candidate[0][1][0] == c_pivot:
            s = 0
            t = 0
            full_evaluation_count = full_evaluation_count + 1
            # copmute the num of all of weights in all terms
            while t < len(tmp_candidate) and tmp_candidate[t][1][0] == c_pivot:
                s = s + tmp_candidate[t][1][1]
                curDID = tmp_candidate[t][0]
                tmp_candidate[t] = (tmp_candidate[t][0], next_posting(candidates[curDID]))
                t = t + 1
            # Get topk resluts, make sure that the length of answers is equal to k
            if s > threshold:
                Ans.append((s, c_pivot))
                if len(Ans) > top_k:
                    Ans.sort(key=lambda x: (-x[0], x[1]))
                    Ans.pop(-1)
                    threshold = Ans[-1][0]
        else:
            # improve the data in tem_cadidates, iterate the terms
            for i in range(pivot):
                (curDID, j) = tmp_candidate[i]
                if j[0] != c_pivot:
                    tmp_candidate[i] = (curDID, seek_to_document(candidates[curDID], c_pivot))

        # break the while, if the sum of weight in tmp_candidates <= 0, there is no object in tmp_candidates
        result_list = []
        for obje in tmp_candidate:
            result_list.append(obje[1][1])
        if sum(result_list) <= 0:
            correct = False
        threshold_list = []
        threshold_list.append(threshold)

    return Ans, full_evaluation_count
