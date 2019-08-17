#pragma once
#ifndef _ASTAR_H_
#define _ASTAR_H_

#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <string.h>
#include <iostream>
#include <map>
#include <utility>      // std::pair
///user defined
#include "message.h"
using namespace std;
struct gridnode;
typedef gridnode* gridnodePtr;
struct gridnode {
	gridnodePtr befrom;
	Point point;
	int id; ///1 --> openset, -1 --> closedset, 0 --> not belong two sets
	double gscore;  // cost function 
	double fscore;  // h function
	int   action; //0 --> 不动 1-4 --> 上下左右
	int   value;
	bool  isskip;
	gridnodePtr skip_point;
	std::multimap<double, gridnodePtr>::iterator nodeMapIt;  //record itself
	gridnode(int y, int x)
	{
		id = 0;
		gscore = 0;
		fscore = 10000;
		befrom = NULL;
		point.x = x;
		point.y = y;
		value = 0;
		action = 0;
		isskip = false;
		skip_point = NULL;
	}
	gridnode() {
		id = 0;
		gscore = 0;
		fscore = 10000;
		befrom = NULL;
		point.x = 0;
		point.y = 0;
		value = 0;
		action = 0;
		isskip = false;
		skip_point = NULL;
	};
	~gridnode() {};
};
class astar
{
public:
	astar() {};
	~astar() {
		delete start_pt;
		delete end_pt;
		delete[] GridNodeMap;
	};
	int path_search(Point st, Point et);
	double getManh(gridnodePtr p1, gridnodePtr p2);
	std::vector<gridnodePtr> retrive_path(gridnodePtr cur_pt);
	void initmap();
	void reset();
public:
	gridnodePtr start_pt = new gridnode();
	gridnodePtr end_pt = new gridnode();
	std::multimap<double, gridnodePtr> openSet;
	gridnodePtr ** GridNodeMap;
};
#endif

