#pragma once
#ifndef _MESSAGE_H_
#define _MESSAGE_H_

#include <string.h>
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <iostream>

struct Point {
	int x;
	int y;
	
	bool operator==(const Point& p) {
		return (x == p.x && y == p.y);
	}
};

struct TeamInfo {
	int id;
	int players[4];
	char* force;
};

struct WormholePair {
	int name1;
	int name2;
	Point point1;
	Point point2;
};

struct Tunnel {
	Point point;
	int direct;//上下左右 20 21 22 23
};

struct Power {
	Point point;
	int value;
};


struct GameMap {
	int h;
	int w;
	
	int map[25][25];
};

struct PlayerInfo {
	int id;
	int score;
	int sleep;
	int team;
	Point point;
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
	void InitMap(int y, int x);
	void UpdateMap(std::vector<Power> powers, std::vector<PlayerInfo> playerInfos);
	void PrintMap();
	void PrintMap2();

public:
	std::vector<Power> mPowers;//已经找到的得分点的坐标保存下来
	int w;//X
	int h;//Y
	

	//      Y   X
	int map[25][25] = {0};  //原始地图，只更新power信息
	int map2[25][25] = {0}; //动态地图，只实时更新player信息
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
	void GenerateMap(int h, int w);                      //当所有信息都生成后，用这个生成map信息
private:

public:
	char* DIRECTLOG[4] = { "UP", "DOWN", "LEFT", "RIGHT" };

    cJSON* root;
	int h;
	int w;
	TeamInfo mTeamInfo;
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



