#pragma once
#ifndef _MESSAGE_H_
#define _MESSAGE_H_

#include <cmath>
#include <string.h>
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <iostream>
#include <core.h>
struct GameMap {
	int h;
	int w;
	int map[25][25];
};

enum DIRECT
{
	MOVE_UP = 0,
	MOVE_DOWN = 1,
	MOVE_LEFT = 2,
	MOVE_RIGHT = 3,
	NO_MOVE = 4,
	
	UP = 20,
	DOWN = 21,
	LEFT = 22,
	RIGHT = 23
};

struct SubAction
{
	DIRECT moveDirect;
};


/*****************************************************
* 全局地图
* 1、因为涉及到类之间的交互，
* 2、当搜集到得分点后，需要管理得分点的坐标，全局地图只展示地图信息
* 3、全局地图中维护一个动态地图，作为场地当前信息
* 4、全局地图只有一个，因此使用单例


0：地图可行区域
1 - 5：分数奖励
10 - 17：player信息
8：障碍物
虫洞id的ascii码：表示虫洞对
20 - 23表示滑梯的上下左右

map能装25x25个数，用w和h对map做约束
******************************************************/
class GlobalMap {

// singleton
public:
	~GlobalMap() {}
	GlobalMap(const GlobalMap&) = delete;
	GlobalMap& operator=(const GlobalMap&) = delete;
	static GlobalMap& Instance() {
		static GlobalMap instance;
		return instance;
	}
private:
	GlobalMap(){}//构造函数私有化
// singleton
public:
	void InitMap(int y, int x, int v);
	void UpdateMap(std::vector<Power> powers, std::vector<PlayerInfo> playerInfos, int round, int mode);
	void PrintMap();
	void PrintMap2();
	bool IsOurPower() { return ourTeamInfo.force == mMode; } // 是否当前为我方优势

public:
	std::vector<Power> mPowers;//已经找到的得分点的坐标保存下来
	std::vector<WormholePair> mWormholePairs; // 虫洞
	std::vector<Tunnel> mTunnels; //通道
	int w;//X
	int h;//Y

	TeamInfo ourTeamInfo;

	//      Y   X
	int map[25][25] ;  //原始地图，只更新power信息
	int map2[25][25]; //动态地图，只实时更新player信息

	//round
	std::vector<PlayerInfo> ourPlayerInfo; // 我方队员信息
	std::vector<PlayerInfo> oppPlayerInfo; // 视野内敌方队员信息
	int mMode; // 表示当前优势能力 0 表示think，1表示beat
	int roundId;
	int vision; // 视野范围

};


/************************
*         ActMsg
************************/

class ActMsg
{
public:
    ActMsg(int roundId);
    ~ActMsg(){cJSON_Delete(root);}
    void AddSubAction(int team, int player, SubAction& act);

    void PackActMsg(char* actMsg, int maxMsgLenth);
public:
    cJSON* root;
    cJSON* msg_data;
    cJSON* actions;
    cJSON* subAct;
    cJSON* move;
	const char* DirectCommand[5] = { "up","down","left","right","" };

};

/************************
*         LegStartMsg
************************/

class LegStartMsg
{
public:
    LegStartMsg(cJSON* msg){root = msg;};
    ~LegStartMsg(){cJSON_Delete(root);};

    void DecodeMessge(int& myTeamId,int myPlayerId[4]);
    void GetMyTeamInfo(int& myTeamId,int myPlayerId[4]); //更新了mTeamInfo信息
    void GetMeteor(int& myTeamId);                       //更新了mMeteors信息
    void GetWormhole(int& myTeamId);                     //更新了mWormholes信息
    void GetTunnel(int& myTeamId);                       //更新了mTunnels信息
    void GetCloud(int& myTeamId);                        //协议里应该是没有这个的
	void GenerateMap(int h, int w, int v);                      //当所有信息都生成后，用这个生成map信息
private:

public:
	char* DIRECTLOG[4] = { "UP", "DOWN", "LEFT", "RIGHT" };

    cJSON* root;
	int h;
	int w;
	TeamInfo mTeamInfo;       //我方teaminfo
	std::vector<Point> mMeteors;
	std::vector<WormholePair> mWormholePairs;
	std::vector<Tunnel> mTunnels;
};

/************************
*         RoundMsg
************************/

class RoundMsg
{
public:
    RoundMsg(cJSON* msg){root = msg;}
    ~RoundMsg(){cJSON_Delete(root);}
    void DecodeMessge();
    int GetRoundId(){return round_id;}
private:
    void DecodePlayers(cJSON *players);
    void DecodeTeams(cJSON *teams);   
    void DecodePower(cJSON *coins);
	void UpdateMap();

public:
    cJSON* root;
    int round_id;
	int mode;
	std::vector<Power> powers;
	std::vector<PlayerInfo> playerInfos;
};

/************************
*         LegEndMsg
************************/
class LegEndMsg
{
public:
    LegEndMsg(cJSON* msg){root = msg;}
    ~LegEndMsg(){cJSON_Delete(root);}
    void DecodeMessge(){};
public:
    cJSON* root;
};

/************************
*         GameEndMsg
************************/
class GameEndMsg
{
public:
    GameEndMsg(cJSON* msg){root = msg;}
    ~GameEndMsg(){cJSON_Delete(root);}
    void DecodeMessge(){}
public:
    cJSON* root;
};

/// 

#endif



