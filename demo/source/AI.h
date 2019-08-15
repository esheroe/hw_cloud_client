#pragma once
#ifndef _AI_H_
#define _AI_H_

#include "message.h"
/*
* 1、处理的信息，然后做出决策
* 2、AI负责管理四个player的行动
*/

class AI
{
public:
	AI();
	~AI();

	// 输入相邻坐标，返回方向，如果坐标不相邻返回 -1
	int moveTo(Point target);
	int moveTo(DIRECT direct);

	void update(); // 更新所有的消息
	void Vision();
	void updateState(); // 更新状态机
	void run();

public:
	Point mPoint; // 自己的坐标
	int id;       // 自己的id 和player相同

	enum STATE {
		SEARCH_MAP, //搜寻地图
		RUN_AWAY,   // 逃跑
		ROUND_UP,   //围捕
		SELF_KILL,  //自杀
	};
};

#endif// _AI_H_
