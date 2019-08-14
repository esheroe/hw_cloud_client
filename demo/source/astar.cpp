#include "astar.h"
std::vector<gridnodePtr> astar::path_search(Point st, Point et)
{
	start_pt = GridNodeMap[st.y][st.x];  
	end_pt = GridNodeMap[et.y][et.x];
	std::vector<gridnodePtr> path;
	path.clear();
	if (grid_map.map[end_pt->point.y][end_pt->point.x] == 8)
		return path;
	gridnodePtr current = NULL;
	gridnodePtr neighbor = NULL;
	start_pt->befrom = NULL;
	start_pt->gscore = 0;
	start_pt->fscore = getManh(start_pt, end_pt);
	start_pt->id = 1;
	start_pt->action = 0;
	openSet.clear();
	start_pt->nodeMapIt = openSet.insert(make_pair(start_pt->fscore, start_pt));
	while (!openSet.empty())
	{
		current = openSet.begin()->second;
		/// arrive at the target point 
		if (current->point == end_pt->point)
		{
			std::cout << "find path " << std::endl;
			return retrive_path(current);
		}
		else
		{
			openSet.erase(openSet.begin());
			current->id = -1; // closed set
			for(int dx = -1; dx < 2; dx++)
				for (int dy = -1; dy < 2; dy++)
				{
					if (0 != dx * dy || (0 == dx && 0 == dy))
						continue;
					neighbor = GridNodeMap[current->point.y + dy][current->point.x + dx];
					// obstacle
					if (8 == grid_map.map[neighbor->point.y][neighbor->point.x])
						continue;
					// the node is in the closed set
					if (-1 == neighbor->id)
						continue;
					double static_cost = 1.0;
					if (1 != neighbor->id)
					{
						neighbor->id = 1;
						neighbor->befrom = current;
						neighbor->gscore = current->gscore + static_cost;
						neighbor->fscore = current->gscore + getManh(neighbor, end_pt);
						neighbor->nodeMapIt = openSet.insert(make_pair(neighbor->fscore, neighbor));
					}
					else if(current->gscore + static_cost<=neighbor->gscore)
					{
						neighbor->befrom = current;
						neighbor->gscore = current->gscore + static_cost;
						neighbor->fscore = current->gscore + getManh(neighbor, end_pt);
						openSet.erase(neighbor->nodeMapIt);
						neighbor->nodeMapIt = openSet.insert(make_pair(neighbor->fscore, neighbor));
					}
				}
			//上方节点 对应action  1
			if (neighbor->point.y < current->point.y)
				neighbor->action = 1;
			//下方节点 对应action  2
			else if (neighbor->point.y > current->point.y)
				neighbor->action = 2;
			//左侧节点 对应action  3
			else if (neighbor->point.x < current->point.x)
				neighbor->action = 3;
			//右侧节点 对应action  4
			else
				neighbor->action = 4;
			//if the neighbor is a tunnel or a warmhole
			if (grid_map.map[neighbor->point.y][neighbor->point.y] > 18)
			{

			}



		}
	}
}

double astar::getManh(gridnodePtr p1, gridnodePtr p2)
{
	return fabs(p1->point.x - p2->point.x) + fabs(p1->point.y - p2->point.y);
}

std::vector<gridnodePtr> astar::retrive_path(gridnodePtr cur_pt)
{
	std::vector<gridnodePtr> path;
	gridnodePtr tmp = cur_pt;
	while (NULL != tmp->befrom)
	{
		path.push_back(tmp);
		tmp = tmp->befrom;
	}
	return path; //obviously, the path does not include the start point
}
void astar::initmap()
{
	GridNodeMap = new gridnodePtr * [grid_map.h];
	//构建指针地图
	for (int i = 0; i < grid_map.h; i++)
	{
		GridNodeMap[i] = new gridnodePtr[grid_map.w];
		for (int j = 0; j < grid_map.w; j++)
		{
			GridNodeMap[i][j] = new gridnode(i, j);
			GridNodeMap[i][j]->value = grid_map.map[i][j];
			/*
			0：地图可行区域
			1 - 5：分数奖励
			10 - 17：player信息
			8：障碍物
			虫洞id的ascii码：表示虫洞对
			20 - 23表示滑梯的上下左右
			h->y
			w->x
			*/
			if (18 < GridNodeMap[i][j]->value)
			{
				GridNodeMap[i][j]->isskip = true;
			}
		}
	}
	//处理时空隧道和虫洞
	for(int i = 0; i < grid_map.h; i++)
		for (int j = 0; j < grid_map.w; j++)
		{
			//处理时空隧道
			if (true == GridNodeMap[i][j]->isskip && GridNodeMap[i][j]->value < 24)
			{
				gridnodePtr current = GridNodeMap[i][j];
				while (current->isskip )
				{
					if (NULL != current->skip_point)
					{
						current = current->skip_point;
						break;
					}
					if (20 == current->value)
						current = GridNodeMap[current->point.y - 1][current->point.x];
					else if (21 == GridNodeMap[i][j]->value)
						current = GridNodeMap[current->point.y + 1][current->point.x];
					else if (22 == GridNodeMap[i][j]->value)
						current = GridNodeMap[current->point.y][current->point.x - 1];
					else if (23 == GridNodeMap[i][j]->value)
						current = GridNodeMap[current->point.y][current->point.x + 1];
				}
				GridNodeMap[i][j]->skip_point = current;
			}
			//处理时空隧道
			else
			{

			}
		}
};