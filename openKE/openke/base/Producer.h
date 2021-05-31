//#ifndef TEST_H
//#define TEST_H
#include "Setting.h"
#include "Reader.h"
#include "Corrupt.h"
//#include "test.h"
#include <iostream>
/*=====================================================================================
link prediction
======================================================================================*/

extern "C"
void produceHead(REAL *con, INT *order, INT lastHead, REAL threshold, bool type_constrain = false) {
    INT h = testList[lastHead].h;
    INT t = testList[lastHead].t;
    INT r = testList[lastHead].r;
    INT lef, rig;
    if (type_constrain) {
        lef = head_lef[r];
        rig = head_rig[r];
    }
    REAL minimal = con[h] + threshold;
    INT initValue = -999;
    INT results[10];
    for (INT x = 0; x < 10; x++) {
        results[x] = initValue;
    }
    INT count = 0;
    for (INT jj = 0; jj < entityTotal; jj++) {
        INT j = order[jj];
        if (j != h) {
            REAL value = con[j];
            if (type_constrain) {
                while (lef < rig && head_type[lef] < j) lef ++;
                if (lef < rig && j == head_type[lef] && not _find(j, t, r)) {
                    if(value < minimal && count < 10) {
                        results[count] = j;
                        count++;
                    } else {
                        break;
                    }
                }
            }
            else {
                    if (not _find(j, t, r)) {
                        if (value < minimal && count < 10) {
                            results[count] = j;
                            count++;
                        } else {
                            break;
                        }
                    }
                }
        }
    }
    FILE *fptr;
    fptr = fopen(outPath.c_str(),"a");
    if(fptr == NULL)
    {
        printf("Error!");
        exit(1);
    }
    for(INT i = 0; i < 10; i++) {
        INT j = results[i];
        if (j != initValue) {
//            std::cout<< j << " " << t << " " << r << " " << con[j] << "\n";
            fprintf(fptr, "%ld\t%ld\t%ld\t%f\n", j, t, r, con[j]);
        } else {
            break;
        }
    }
    fclose(fptr);
}

extern "C"
void produceTail(REAL *con, INT *order, INT lastTail, REAL threshold, bool type_constrain = false) {
    INT h = testList[lastTail].h;
    INT t = testList[lastTail].t;
    INT r = testList[lastTail].r;
    INT lef, rig;
    if (type_constrain) {
        lef = tail_lef[r];
        rig = tail_rig[r];
    }

    REAL minimal = con[t] + threshold;
    INT initValue = -999;
    INT results[10];
    for (INT x = 0; x < 10; x++) {
        results[x] = initValue;
    }
    INT count = 0;
    for (INT jj = 0; jj < entityTotal; jj++) {
        INT j = order[jj];
        if (j != t) {
            REAL value = con[j];
            if (type_constrain) {
                while (lef < rig && tail_type[lef] < j) lef ++;
                if (lef < rig && j == tail_type[lef] && not _find(h, j, r)) {
                    if(value < minimal && count < 10) {
                        results[count] = j;
                        count++;
                    } else {
                        break;
                    }
                }
            }
            else {
                    if (not _find(h, j, r)) {
                        if (value < minimal && count < 10) {
                            results[count] = j;
                            count++;
                        } else {
                            break;
                        }
                    }
                }
        }
    }
    FILE *fptr;
    fptr = fopen(outPath.c_str(),"a");
    if(fptr == NULL)
    {
        printf("Error!");
        exit(1);
    }
    for(INT i = 0; i < 10; i++) {
        INT j = results[i];
        if (j != initValue) {
//            std::cout<< h << " " << j << " " << r << " " << con[j] << "\n";
            fprintf(fptr, "%ld\t%ld\t%ld\t%f\n", j, t, r, con[j]);
        } else {
            break;
        }
    }
    fclose(fptr);
}

extern "C"
void produceRel(REAL *con) {
    INT h = testList[lastRel].h;
    INT t = testList[lastRel].t;
    INT r = testList[lastRel].r;

    REAL minimal = con[r];
    INT rel_s = 0;
    INT rel_filter_s = 0;

    for (INT j = 0; j < relationTotal; j++) {
        if (j != r) {
            REAL value = con[j];
            if (value < minimal) {
                rel_s += 1;
                if (not _find(h, t, j))
                    rel_filter_s += 1;
            }
        }
    }

    if (rel_filter_s < 10) rel_filter_tot += 1;
    if (rel_s < 10) rel_tot += 1;
    if (rel_filter_s < 3) rel3_filter_tot += 1;
    if (rel_s < 3) rel3_tot += 1;
    if (rel_filter_s < 1) rel1_filter_tot += 1;
    if (rel_s < 1) rel1_tot += 1;

    rel_filter_rank += (rel_filter_s+1);
    rel_rank += (1+rel_s);
    rel_filter_reci_rank += 1.0/(rel_filter_s+1);
    rel_reci_rank += 1.0/(rel_s+1);

    lastRel++;
}


