#ifndef _CORE_H_
#define _CORE_H_
#include "message.h"
struct Point {
	int x;
	int y;

	bool operator==(const Point& p) {
		return (x == p.x && y == p.y);
	}
	Point& operator=(const Point& p)
	{
		x = p.x;
		y = p.y;
		return *this;
	}
	Point(int x_, int y_) { x = x_; y = y_; }
	Point() {};
};

// 表示队伍优势能力 0 表示think，1表示beat
struct TeamInfo {
	int id;
	int players[4];
	int force;

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
struct PlayerInfo {
	int id;
	int score;
	int sleep;
	int team;
	Point point;
};

/*int getdis(Point p1, Point p2)
{
	return int(fabs(p1.x - p2.x)) + int(fabs(p1.y - p2.y));
}*/

#endif // !_CORE_H_


