#include "AI.h"
AI::AI()
{
}
AI::~AI()
{
}
void AI::init(int id_,int vision_)
{
	isvalid = true;
	id = id_;
	vision = vision_;
}
void AI::update()
{
	GlobalMap& globalMap = GlobalMap::Instance();
	isvalid = false;
	for (auto pinfo : globalMap.ourPlayerInfo)
	{
		if (pinfo.id == id)
		{
			isvalid = true;
			mPoint = pinfo.point;

		}
	}
}

Point AI::gettarget()
{
	GlobalMap& globalMap = GlobalMap::Instance();
	//for(auto )
	return waypoints[0];
}

void AI::run()
{
	target = waypoints[0];
}

void Team::init(TeamInfo teaminfo,int vision)
{
	///对应0，1，2，3号
	stupid.init(teaminfo.players[0], vision);
	idiot.init(teaminfo.players[1], vision);
	fool.init(teaminfo.players[2], vision);
	git.init(teaminfo.players[3], vision);
	//0号的初始巡逻路线
	stupid.waypoints.push_back(Point(3, 13));
	stupid.waypoints.push_back(Point(3, 8));
	stupid.waypoints.push_back(Point(3, 3));
	stupid.waypoints.push_back(Point(8, 3));
	stupid.waypoints.push_back(Point(13, 3));
	

	//1号的初始巡逻路线
	git.waypoints.push_back(Point(13, 16));
	git.waypoints.push_back(Point(8, 16));
	git.waypoints.push_back(Point(3, 16));

	//2号的初始巡逻路线
	fool.waypoints.push_back(Point(12, 8));
	fool.waypoints.push_back(Point(10, 10));
	fool.waypoints.push_back(Point(8, 12));

	//3号的巡逻路线
	idiot.waypoints.push_back(Point(16, 3));
	idiot.waypoints.push_back(Point(16, 8));
	idiot.waypoints.push_back(Point(16, 13));
	idiot.waypoints.push_back(Point(16, 16));
}
void Team::update()
{
	std::cout << "update " << std::endl;
	stupid.update();
	idiot.update();
	fool.update();
	git.update();
}
void Team::process()
{
	stupid.run();
	idiot.run();
	fool.run();
	git.run();
}
void Team::power_allocation(std::vector<Power> powers)
{
	for (auto pw : powers)
	{
		
	}
}