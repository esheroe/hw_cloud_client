#pragma once
#ifndef _AI_H_
#define _AI_H_

#include "message.h"
/*
* 1���������Ϣ��Ȼ����������
* 2��AI��������ĸ�player���ж�
*/

class AI
{
public:
	AI();
	~AI();

	// �����������꣬���ط���������겻���ڷ��� -1
	int moveTo(Point target) ;
	int moveTo(DIRECT direct);
	void init(int id_,int vision_);
	void update(); // �������е���Ϣ
	void Vision();
	void updateState(); // ����״̬��
	void run();

public:
	bool isvalid;  //�������Ƿ���
	Point mPoint;  // �Լ�������
	int id;        // �Լ���id ��player��ͬ
	int vision;    //��Ұ
	std::vector<Point> waypoints;
	std::vector<Power> powers;
	int visted_num = 0;
	Point target;
	
	enum STATE {
		SEARCH_MAP, //��Ѱ��ͼ
		RUN_AWAY,   // ����
		ROUND_UP,   //Χ��
		SELF_KILL,  //��ɱ
	};
};
class Team
{
public:
	Team() {};
	void init(TeamInfo teaminfo,int vision);
	void update();
	void process();
	~Team() {};
	void power_allocation(std::vector<Power> powers);
public:
	AI stupid;
	AI idiot;
	AI fool;
	AI git;
};

#endif// _AI_H_
