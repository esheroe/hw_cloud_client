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
	int moveTo(Point target);
	int moveTo(DIRECT direct);

	void update(); // �������е���Ϣ
	void Vision();
	void updateState(); // ����״̬��
	void run();

public:
	Point mPoint; // �Լ�������
	int id;       // �Լ���id ��player��ͬ

	enum STATE {
		SEARCH_MAP, //��Ѱ��ͼ
		RUN_AWAY,   // ����
		ROUND_UP,   //Χ��
		SELF_KILL,  //��ɱ
	};
};

#endif// _AI_H_
