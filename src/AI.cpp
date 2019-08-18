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
	std::cout << " id" << id << powers.size() << std::endl;;
	if (powers.empty())
	{
		target = waypoints[visted_num];
		if (mPoint == waypoints[visted_num])
		{
			visted_num++;
			if (visted_num >= waypoints.size())
				visted_num = 0;
		}
	}
	else
	{
		std::cout << "choose powers" << std::endl;
		target = powers[0].point;
	}
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
	fool.waypoints.push_back(Point(11, 8));
	fool.waypoints.push_back(Point(10, 10));
	fool.waypoints.push_back(Point(8, 11));

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
void Team::power_allocation(std::vector<Power> powers_)
{
	stupid.powers.clear();
	idiot.powers.clear();
	fool.powers.clear();
	git.powers.clear();
	for (auto pw : powers_)
	{
		if (getdis(pw.point, stupid.mPoint) < stupid.vision)
		{
			stupid.powers.push_back(pw);
			continue;
		}
		if (getdis(pw.point, idiot.mPoint) < idiot.vision)
		{
			idiot.powers.push_back(pw);
			continue;
		}
		if (getdis(pw.point, fool.mPoint) < fool.vision)
		{
			fool.powers.push_back(pw);
			continue;
		}
		if (getdis(pw.point, git.mPoint) < git.vision)
		{
			git.powers.push_back(pw);
			continue;
		}
	}
}
int Team::getdis(Point p1, Point p2)
{
	if (fabs(p1.x - p2.x) > fabs(p1.y - p2.y))
		return fabs(p1.x - p2.x);
	else
		return fabs(p1.y - p2.y);
}