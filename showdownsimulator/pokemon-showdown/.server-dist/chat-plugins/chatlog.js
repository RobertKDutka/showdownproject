"use strict";Object.defineProperty(exports, "__esModule", {value: true}); function _optionalChain(ops) { let lastAccessLHS = undefined; let value = ops[0]; let i = 1; while (i < ops.length) { const op = ops[i]; const fn = ops[i + 1]; i += 2; if ((op === 'optionalAccess' || op === 'optionalCall') && value == null) { return undefined; } if (op === 'access' || op === 'optionalAccess') { lastAccessLHS = value; value = fn(value); } else if (op === 'call' || op === 'optionalCall') { value = fn((...args) => value.call(lastAccessLHS, ...args)); lastAccessLHS = undefined; } } return value; }/**
 * Pokemon Showdown log viewer
 *
 * by Zarel
 * @license MIT
 */

var _lib = require('../../.lib-dist');
var _configloader = require('../config-loader');
var _dex = require('../../.sim-dist/dex');
var _chat = require('../chat');

const DAY = 24 * 60 * 60 * 1000;
const MAX_RESULTS = 3000;
const MAX_MEMORY = 67108864; // 64MB
const MAX_PROCESSES = 1;
const MAX_TOPUSERS = 100;

const CHATLOG_PM_TIMEOUT = 1 * 60 * 60 * 1000; // 1 hour

const UPPER_STAFF_ROOMS = ['upperstaff', 'adminlog', 'slowlog'];










 class LogReaderRoom {
	
	constructor(roomid) {
		this.roomid = roomid;
	}

	async listMonths() {
		try {
			const listing = await _lib.FS.call(void 0, `logs/chat/${this.roomid}`).readdir();
			return listing.filter(file => /^[0-9][0-9][0-9][0-9]-[0-9][0-9]$/.test(file));
		} catch (err) {
			return [];
		}
	}

	async listDays(month) {
		try {
			const listing = await _lib.FS.call(void 0, `logs/chat/${this.roomid}/${month}`).readdir();
			return listing.filter(file => file.endsWith(".txt")).map(file => file.slice(0, -4));
		} catch (err) {
			return [];
		}
	}

	async getLog(day) {
		const month = exports.LogReader.getMonth(day);
		const log = _lib.FS.call(void 0, `logs/chat/${this.roomid}/${month}/${day}.txt`);
		if (!await log.exists()) return null;
		return log.createReadStream();
	}
} exports.LogReaderRoom = LogReaderRoom;

 const LogReader = new class {
	async get(roomid) {
		if (!await _lib.FS.call(void 0, `logs/chat/${roomid}`).exists()) return null;
		return new LogReaderRoom(roomid);
	}

	async list() {
		const listing = await _lib.FS.call(void 0, `logs/chat`).readdir();
		return listing.filter(file => /^[a-z0-9-]+$/.test(file)) ;
	}

	async listCategorized(user, opts) {
		const list = await this.list();
		const isUpperStaff = user.can('rangeban');
		const isStaff = user.can('lock');

		const official = [];
		const normal = [];
		const hidden = [];
		const secret = [];
		const deleted = [];
		const personal = [];
		const deletedPersonal = [];
		let atLeastOne = false;

		for (const roomid of list) {
			const room = Rooms.get(roomid);
			const forceShow = room && (
				// you are authed in the room
				(room.auth.has(user.id) && user.can('mute', null, room)) ||
				// you are staff and currently in the room
				(isStaff && user.inRooms.has(room.roomid))
			);
			if (!isUpperStaff && !forceShow) {
				if (!isStaff) continue;
				if (!room) continue;
				if (!room.checkModjoin(user)) continue;
				if (room.settings.isPrivate === true) continue;
			}

			atLeastOne = true;
			if (roomid.includes('-')) {
				const matchesOpts = opts && roomid.startsWith(`${opts}-`);
				if (matchesOpts || opts === 'all' || forceShow) {
					(room ? personal : deletedPersonal).push(roomid);
				}
			} else if (!room) {
				if (opts === 'all' || opts === 'deleted') deleted.push(roomid);
			} else if (room.settings.section === 'official') {
				official.push(roomid);
			} else if (!room.settings.isPrivate) {
				normal.push(roomid);
			} else if (room.settings.isPrivate === 'hidden') {
				hidden.push(roomid);
			} else {
				secret.push(roomid);
			}
		}

		if (!atLeastOne) return null;
		return {official, normal, hidden, secret, deleted, personal, deletedPersonal};
	}

	async read(roomid, day, limit) {
		const roomLog = await exports.LogReader.get(roomid);
		const stream = await roomLog.getLog(day);
		let buf = '';
		let i = (exports.LogSearcher ).results || 0;
		if (!stream) {
			buf += `<p class="message-error">Room "${roomid}" doesn't have logs for ${day}</p>`;
		} else {
			for await (const line of stream.byLine()) {
				const rendered = exports.LogViewer.renderLine(line);
				if (rendered) {
					buf += `${line}\n`;
					i++;
					if (i > limit) break;
				}
			}
		}
		return buf;
	}
	getMonth(day) {
		if (!day) day = _chat.Chat.toTimestamp(new Date()).split(' ')[0];
		return day.slice(0, 7);
	}
	nextDay(day) {
		const nextDay = new Date(new Date(day).getTime() + DAY);
		return nextDay.toISOString().slice(0, 10);
	}
	prevDay(day) {
		const prevDay = new Date(new Date(day).getTime() - DAY);
		return prevDay.toISOString().slice(0, 10);
	}
	nextMonth(month) {
		const nextMonth = new Date(new Date(`${month}-15`).getTime() + 30 * DAY);
		return nextMonth.toISOString().slice(0, 7);
	}
	prevMonth(month) {
		const prevMonth = new Date(new Date(`${month}-15`).getTime() - 30 * DAY);
		return prevMonth.toISOString().slice(0, 7);
	}
	today() {
		return _chat.Chat.toTimestamp(new Date()).slice(0, 10);
	}
	isMonth(text) {
		return /[0-9]{4}-[0-9]{2}/.test(text);
	}
	isDay(text) {
		return /[0-9]{4}-[0-9]{2}-[0-9]{2}/.test(text);
	}
	async findBattleLog(tier, number) {
		// binary search!
		const months = (await _lib.FS.call(void 0, 'logs').readdir()).filter(this.isMonth).sort();
		if (!months.length) return null;

		// find first day
		let firstDay;
		while (months.length) {
			const month = months[0];
			try {
				const days = (await _lib.FS.call(void 0, `logs/${month}/${tier}/`).readdir()).filter(this.isDay).sort();
				firstDay = days[0];
				break;
			} catch (err) {}
			months.shift();
		}
		if (!firstDay) return null;

		// find last day
		let lastDay;
		while (months.length) {
			const month = months[months.length - 1];
			try {
				const days = (await _lib.FS.call(void 0, `logs/${month}/${tier}/`).readdir()).filter(this.isDay).sort();
				lastDay = days[days.length - 1];
				break;
			} catch (err) {}
			months.pop();
		}
		if (!lastDay) throw new Error(`getBattleLog month range search for ${tier}`);

		const getBattleNum = (battleName) => Number(battleName.split('-')[1].slice(0, -9));

		const getDayRange = async (day) => {
			const month = day.slice(0, 7);

			try {
				const battles = (await _lib.FS.call(void 0, `logs/${month}/${tier}/${day}`).readdir()).filter(
					b => b.endsWith('.log.json')
				);
				_lib.Utils.sortBy(battles, getBattleNum);

				return [getBattleNum(battles[0]), getBattleNum(battles[battles.length - 1])];
			} catch (err) {
				return null;
			}
		};

		const dayExists = (day) => _lib.FS.call(void 0, `logs/${day.slice(0, 7)}/${tier}/${day}`).exists();

		const nextExistingDay = async (day) => {
			for (let i = 0; i < 3650; i++) {
				day = this.nextDay(day);
				if (await dayExists(day)) return day;
				if (day === lastDay) return null;
			}
			return null;
		};

		const prevExistingDay = async (day) => {
			for (let i = 0; i < 3650; i++) {
				day = this.prevDay(day);
				if (await dayExists(day)) return day;
				if (day === firstDay) return null;
			}
			return null;
		};

		for (let i = 0; i < 100; i++) {
			const middleDay = new Date(
				(new Date(firstDay).getTime() + new Date(lastDay).getTime()) / 2
			).toISOString().slice(0, 10);

			let currentDay = middleDay;
			let dayRange = await getDayRange(middleDay);

			if (!dayRange) {
				currentDay = await nextExistingDay(middleDay);
				if (!currentDay) {
					const lastExistingDay = await prevExistingDay(middleDay);
					if (!lastExistingDay) throw new Error(`couldn't find existing day`);
					lastDay = lastExistingDay;
					continue;
				}
				dayRange = await getDayRange(currentDay);
				if (!dayRange) throw new Error(`existing day was a lie`);
			}

			const [lowest, highest] = dayRange;

			if (number < lowest) {
				// before currentDay
				if (firstDay === currentDay) return null;
				lastDay = this.prevDay(currentDay);
			} else if (number > highest) {
				// after currentDay
				if (lastDay === currentDay) return null;
				firstDay = this.nextDay(currentDay);
			} else {
				// during currentDay
				const month = currentDay.slice(0, 7);
				const path = _lib.FS.call(void 0, `logs/${month}/${tier}/${currentDay}/${tier}-${number}.log.json`);
				if (await path.exists()) {
					return JSON.parse(path.readSync()).log;
				}
				return null;
			}
		}

		// 100 iterations is enough to search 2**100 days, which is around 1e30 days
		// for comparison, a millennium is 365000 days
		throw new Error(`Infinite loop looking for ${tier}-${number}`);
	}
}; exports.LogReader = LogReader;

 const LogViewer = new class {
	async day(roomid, day, opts) {
		const month = exports.LogReader.getMonth(day);
		let buf = `<div class="pad"><p>` +
			`<a roomid="view-chatlog">◂ All logs</a> / ` +
			`<a roomid="view-chatlog-${roomid}">${roomid}</a> /  ` +
			`<a roomid="view-chatlog-${roomid}--${month}">${month}</a> / ` +
			`<strong>${day}</strong></p><small>${opts ? `Options in use: ${opts}` : ''}</small> <hr />`;

		const roomLog = await exports.LogReader.get(roomid);
		if (!roomLog) {
			buf += `<p class="message-error">Room "${roomid}" doesn't exist</p></div>`;
			return this.linkify(buf);
		}

		const prevDay = exports.LogReader.prevDay(day);
		const prevRoomid = `view-chatlog-${roomid}--${prevDay}${opts ? `--${opts}` : ''}`;
		buf += `<p><a roomid="${prevRoomid}" class="blocklink" style="text-align:center">▲<br />${prevDay}</a></p>` +
			`<div class="message-log" style="overflow-wrap: break-word">`;

		const stream = await roomLog.getLog(day);
		if (!stream) {
			buf += `<p class="message-error">Room "${roomid}" doesn't have logs for ${day}</p>`;
		} else {
			for await (const line of stream.byLine()) {
				buf += this.renderLine(line, opts);
			}
		}
		buf += `</div>`;
		if (day !== exports.LogReader.today()) {
			const nextDay = exports.LogReader.nextDay(day);
			const nextRoomid = `view-chatlog-${roomid}--${nextDay}${opts ? `--${opts}` : ''}`;
			buf += `<p><a roomid="${nextRoomid}" class="blocklink" style="text-align:center">${nextDay}<br />▼</a></p>`;
		}

		buf += `</div>`;
		return this.linkify(buf);
	}

	async battle(tier, number, context) {
		if (number > Rooms.global.lastBattle) {
			throw new _chat.Chat.ErrorMessage(`That battle cannot exist, as the number has not been used.`);
		}
		const roomid = `battle-${tier}-${number}` ;
		context.setHTML(`<div class="pad"><h2>Locating battle logs for the battle ${tier}-${number}...</h2></div>`);
		const log = await exports.PM.query({
			queryType: 'battlesearch', roomid: toID(tier), search: number,
		});
		if (!log) return context.setHTML(this.error("Logs not found."));
		const {connection} = context;
		context.close();
		connection.sendTo(
			roomid, `|init|battle\n|title|[Battle Log] ${tier}-${number}\n${log.join('\n')}`
		);
		connection.sendTo(roomid, `|expire|This is a battle log.`);
	}

	renderLine(fullLine, opts) {
		if (!fullLine) return ``;
		if (opts === 'txt') return _lib.Utils.html`<div class="chat">${fullLine}</div>`;
		let timestamp = fullLine.slice(0, opts ? 8 : 5);
		let line;
		if (/^[0-9:]+$/.test(timestamp)) {
			line = fullLine.charAt(9) === '|' ? fullLine.slice(10) : '|' + fullLine.slice(9);
		} else {
			timestamp = '';
			line = '!NT|';
		}
		if (opts !== 'all' && (
			line.startsWith(`userstats|`) ||
			line.startsWith('J|') || line.startsWith('L|') || line.startsWith('N|')
		)) return ``;

		const cmd = line.slice(0, line.indexOf('|'));
		if (_optionalChain([opts, 'optionalAccess', _ => _.includes, 'call', _2 => _2('onlychat')])) {
			if (cmd !== 'c') return '';
			if (opts.includes('txt')) return `<div class="chat">${_lib.Utils.escapeHTML(fullLine)}</div>`;
		}
		switch (cmd) {
		case 'c': {
			const [, name, message] = _lib.Utils.splitFirst(line, '|', 2);
			if (name.length <= 1) {
				return `<div class="chat"><small>[${timestamp}] </small><q>${_chat.Chat.formatText(message)}</q></div>`;
			}
			if (message.startsWith(`/log `)) {
				return `<div class="chat"><small>[${timestamp}] </small><q>${_chat.Chat.formatText(message.slice(5))}</q></div>`;
			}
			if (message.startsWith(`/raw `)) {
				return `<div class="notice">${message.slice(5)}</div>`;
			}
			if (message.startsWith(`/uhtml `) || message.startsWith(`/uhtmlchange `)) {
				if (message.startsWith(`/uhtmlchange `)) return ``;
				if (opts !== 'all') return `<div class="notice">[uhtml box hidden]</div>`;
				return `<div class="notice">${message.slice(message.indexOf(',') + 1)}</div>`;
			}
			const group = !name.startsWith(' ') ? name.charAt(0) : ``;
			return `<div class="chat">` +
				_lib.Utils.html`<small>[${timestamp}] ${group}</small><username>${name.slice(1)}:</username> ` +
				`<q>${_chat.Chat.formatText(message)}</q>` +
				`</div>`;
		}
		case 'html': case 'raw': {
			const [, html] = _lib.Utils.splitFirst(line, '|', 1);
			return `<div class="notice">${html}</div>`;
		}
		case 'uhtml': case 'uhtmlchange': {
			if (cmd !== 'uhtml') return ``;
			const [, , html] = _lib.Utils.splitFirst(line, '|', 2);
			return `<div class="notice">${html}</div>`;
		}
		case '!NT':
			return `<div class="chat">${_lib.Utils.escapeHTML(fullLine)}</div>`;
		case '':
			return `<div class="chat"><small>[${timestamp}] </small>${_lib.Utils.escapeHTML(line.slice(1))}</div>`;
		default:
			return `<div class="chat"><small>[${timestamp}] </small><code>${'|' + _lib.Utils.escapeHTML(line)}</code></div>`;
		}
	}

	async month(roomid, month) {
		let buf = `<div class="pad"><p>` +
			`<a roomid="view-chatlog">◂ All logs</a> / ` +
			`<a roomid="view-chatlog-${roomid}">${roomid}</a> / ` +
			`<strong>${month}</strong></p><hr />`;

		const roomLog = await exports.LogReader.get(roomid);
		if (!roomLog) {
			buf += `<p class="message-error">Room "${roomid}" doesn't exist</p></div>`;
			return this.linkify(buf);
		}

		const prevMonth = exports.LogReader.prevMonth(month);
		buf += `<p><a roomid="view-chatlog-${roomid}--${prevMonth}" class="blocklink" style="text-align:center">▲<br />${prevMonth}</a></p><div>`;

		const days = await roomLog.listDays(month);
		if (!days.length) {
			buf += `<p class="message-error">Room "${roomid}" doesn't have logs in ${month}</p></div>`;
			return this.linkify(buf);
		} else {
			for (const day of days) {
				buf += `<p>- <a roomid="view-chatlog-${roomid}--${day}">${day}</a> <small>`;
				for (const opt of ['txt', 'onlychat', 'all', 'txt-onlychat']) {
					buf += ` (<a roomid="view-chatlog-${roomid}--${day}--${opt}">${opt}</a>) `;
				}
				buf += `</small></p>`;
			}
		}

		if (!exports.LogReader.today().startsWith(month)) {
			const nextMonth = exports.LogReader.nextMonth(month);
			buf += `<p><a roomid="view-chatlog-${roomid}--${nextMonth}" class="blocklink" style="text-align:center">${nextMonth}<br />▼</a></p>`;
		}

		buf += `</div>`;
		return this.linkify(buf);
	}
	async room(roomid) {
		let buf = `<div class="pad"><p>` +
			`<a roomid="view-chatlog">◂ All logs</a> / ` +
			`<strong>${roomid}</strong></p><hr />`;

		const roomLog = await exports.LogReader.get(roomid);
		if (!roomLog) {
			buf += `<p class="message-error">Room "${roomid}" doesn't exist</p></div>`;
			return this.linkify(buf);
		}

		const months = await roomLog.listMonths();
		if (!months.length) {
			buf += `<p class="message-error">Room "${roomid}" doesn't have logs</p></div>`;
			return this.linkify(buf);
		}

		for (const month of months) {
			buf += `<p>- <a roomid="view-chatlog-${roomid}--${month}">${month}</a></p>`;
		}
		buf += `</div>`;
		return this.linkify(buf);
	}
	async list(user, opts) {
		let buf = `<div class="pad"><p>` +
			`<strong>All logs</strong></p><hr />`;

		const categories = {
			'official': "Official",
			'normal': "Public",
			'hidden': "Hidden",
			'secret': "Secret",
			'deleted': "Deleted",
			'personal': "Personal",
			'deletedPersonal': "Deleted Personal",
		};
		const list = await exports.LogReader.listCategorized(user, opts) ;

		if (!list) {
			buf += `<p class="message-error">You must be a staff member of a room to view its logs</p></div>`;
			return buf;
		}

		const showPersonalLink = opts !== 'all' && user.can('rangeban');
		for (const k in categories) {
			if (!list[k].length && !(['personal', 'deleted'].includes(k) && showPersonalLink)) {
				continue;
			}
			buf += `<p>${categories[k]}</p>`;
			if (k === 'personal' && showPersonalLink) {
				if (opts !== 'help') buf += `<p>- <a roomid="view-chatlog--help">(show all help)</a></p>`;
				if (opts !== 'groupchat') buf += `<p>- <a roomid="view-chatlog--groupchat">(show all groupchat)</a></p>`;
			}
			if (k === 'deleted' && showPersonalLink) {
				if (opts !== 'deleted') buf += `<p>- <a roomid="view-chatlog--deleted">(show deleted)</a></p>`;
			}
			for (const roomid of list[k]) {
				buf += `<p>- <a roomid="view-chatlog-${roomid}">${roomid}</a></p>`;
			}
		}
		buf += `</div>`;
		return this.linkify(buf);
	}
	error(message) {
		return `<div class="pad"><p class="message-error">${message}</p></div>`;
	}
	linkify(buf) {
		return buf.replace(/<a roomid="/g, `<a target="replace" href="/`);
	}
}; exports.LogViewer = LogViewer;

/** Match with two lines of context in either direction */


 class Searcher {
	constructUserRegex(user) {
		const id = toID(user);
		return `.${[...id].join('[^a-zA-Z0-9]*')}[^a-zA-Z0-9]*`;
	}
	constructSearchRegex(str) {
		// modified regex replace
		str = str.replace(/[\\^$.*?()[\]{}|]/g, '\\$&');
		const searches = str.split('+');
		if (searches.length <= 1) {
			if (str.length <= 3) return `\b${str}`;
			return str;
		}
		return `^` + searches.filter(Boolean).map(term => `(?=.*${term})`).join('');
	}
	


	renderLinecountResults(
		results,
		roomid, month, user
	) {
		let buf = _lib.Utils.html`<div class="pad"><h2>Linecounts on `;
		buf += `${roomid}${user ? ` for the user ${user}` : ` (top ${MAX_TOPUSERS})`}</h2>`;
		buf += `<strong>Month: ${month}:</strong><br />`;
		const nextMonth = exports.LogReader.nextMonth(month);
		const prevMonth = exports.LogReader.prevMonth(month);
		if (_lib.FS.call(void 0, `logs/chat/${roomid}/${prevMonth}`).existsSync()) {
			buf += `<small><a roomid="view-roomstats-${roomid}--${prevMonth}${user ? `--${user}` : ''}">Previous month</a></small>`;
		}
		if (_lib.FS.call(void 0, `logs/chat/${roomid}/${nextMonth}`).existsSync()) {
			buf += ` <small><a roomid="view-roomstats-${roomid}--${nextMonth}${user ? `--${user}` : ''}">Next month</a></small>`;
		}
		if (!results) {
			buf += '<hr />';
			buf += exports.LogViewer.error(`Logs for month '${month}' do not exist on room ${roomid}.`);
			return buf;
		} else if (user) {
			let total = 0;
			for (const day in results) {
				if (isNaN(results[day][user])) continue;
				total += results[day][user];
			}
			buf += `<br />Total linecount: ${total}<hr />`;
			buf += '<ol>';
			const sortedDays = _lib.Utils.sortBy(Object.keys(results), day => ({reverse: day}));
			for (const day of sortedDays) {
				const dayResults = results[day][user];
				if (isNaN(dayResults)) continue;
				buf += `<li>[<a roomid="view-chatlog-${roomid}--${day}">${day}</a>]: `;
				buf += `${_chat.Chat.count(dayResults, 'lines')}</li>`;
			}
		} else {
			buf += '<hr /><ol>';
			// squish the results together
			const totalResults = {};
			for (const date in results) {
				for (const userid in results[date]) {
					if (!totalResults[userid]) totalResults[userid] = 0;
					totalResults[userid] += results[date][userid];
				}
			}
			const resultKeys = Object.keys(totalResults);
			const sortedResults = _lib.Utils.sortBy(resultKeys, userid => (
				-totalResults[userid]
			)).slice(0, MAX_TOPUSERS);
			for (const userid of sortedResults) {
				buf += `<li><span class="username"><username>${userid}</username></span>: `;
				buf += `${_chat.Chat.count(totalResults[userid], 'lines')}</li>`;
			}
		}
		buf += `</div>`;
		return exports.LogViewer.linkify(buf);
	}
	async runSearch(
		context, search, roomid, date, limit
	) {
		context.title = `[Search] [${roomid}] ${search}`;
		if (!['ripgrep', 'fs'].includes(_configloader.Config.chatlogreader)) {
			throw new Error(`Config.chatlogreader must be 'fs' or 'ripgrep'.`);
		}
		context.setHTML(
			`<div class="pad"><h2>Running a chatlog search for "${search}" on room ${roomid}` +
			(date ? date !== 'all' ? `, on the date "${date}"` : ', on all dates' : '') +
			`.</h2></div>`
		);
		const response = await exports.PM.query({search, roomid, date, limit, queryType: 'search'});
		return context.setHTML(response);
	}
	async runLinecountSearch(context, roomid, month, user) {
		context.setHTML(
			`<div class="pad"><h2>Searching linecounts on room ${roomid}${user ? ` for the user ${user}` : ''}.</h2></div>`
		);
		const results = await exports.PM.query({roomid, date: month, search: user, queryType: 'linecount'});
		context.setHTML(results);
	}
	async sharedBattles(userids) {
		let buf = `Logged shared battles between the users ${userids.join(', ')}`;
		const results = await exports.PM.query({
			queryType: 'sharedsearch', search: userids,
		});
		if (!results.length) {
			buf += `:<br />None found.`;
			return buf;
		}
		buf += ` (${results.length}):<br />`;
		buf += results.map(id => `<a href="view-battlelog-${id}">${id}</a>`).join(', ');
		return buf;
	}
} exports.Searcher = Searcher;

 class FSLogSearcher extends Searcher {
	
	constructor() {
		super();
		this.results = 0;
	}
	async searchLinecounts(roomid, month, user) {
		const directory = _lib.FS.call(void 0, `logs/chat/${roomid}/${month}`);
		if (!directory.existsSync()) {
			return this.renderLinecountResults(null, roomid, month, user);
		}
		const files = await directory.readdir();
		const results = {};
		for (const file of files) {
			const day = file.slice(0, -4);
			const stream = _lib.FS.call(void 0, `logs/chat/${roomid}/${month}/${file}`).createReadStream();
			for await (const line of stream.byLine()) {
				const parts = line.split('|').map(toID);
				const id = parts[2];
				if (!id) continue;
				if (parts[1] === 'c') {
					if (user && id !== user) continue;
					if (!results[day]) results[day] = {};
					if (!results[day][id]) results[day][id] = 0;
					results[day][id]++;
				}
			}
		}
		return this.renderLinecountResults(results, roomid, month, user);
	}
	searchLogs(roomid, search, limit, date) {
		if (!date) date = _chat.Chat.toTimestamp(new Date()).split(' ')[0].slice(0, -3);
		const isAll = (date === 'all');
		const isYear = (date.length === 4);
		const isMonth = (date.length === 7);
		if (!limit || limit > MAX_RESULTS) limit = MAX_RESULTS;
		if (isAll) {
			return this.runYearSearch(roomid, null, search, limit);
		} else if (isYear) {
			date = date.substr(0, 4);
			return this.runYearSearch(roomid, date, search, limit);
		} else if (isMonth) {
			date = date.substr(0, 7);
			return this.runMonthSearch(roomid, date, search, limit);
		} else {
			return Promise.resolve(exports.LogViewer.error("Invalid date."));
		}
	}

	async fsSearchDay(roomid, day, search, limit) {
		if (!limit || limit > MAX_RESULTS) limit = MAX_RESULTS;
		const text = await exports.LogReader.read(roomid, day, limit);
		if (!text) return [];
		const lines = text.split('\n');
		const matches = [];

		const searchTerms = search.split('+').filter(Boolean);
		const searchTermRegexes = [];
		for (const searchTerm of searchTerms) {
			if (searchTerm.startsWith('user-')) {
				const id = toID(searchTerm.slice(5));
				searchTermRegexes.push(new RegExp(`\\|c\\|${this.constructUserRegex(id)}\\|`, 'i'));
				continue;
			}
			searchTermRegexes.push(new RegExp(searchTerm, 'i'));
		}
		function matchLine(line) {
			return searchTermRegexes.every(term => term.test(line));
		}

		for (const [i, line] of lines.entries()) {
			if (matchLine(line)) {
				matches.push([
					lines[i - 2],
					lines[i - 1],
					line,
					lines[i + 1],
					lines[i + 2],
				]);
				if (matches.length > limit) break;
			}
		}
		return matches;
	}

	renderDayResults(results, roomid) {
		const renderResult = (match) => {
			this.results++;
			return (
				exports.LogViewer.renderLine(match[0]) +
				exports.LogViewer.renderLine(match[1]) +
				`<div class="chat chatmessage highlighted">${exports.LogViewer.renderLine(match[2])}</div>` +
				exports.LogViewer.renderLine(match[3]) +
				exports.LogViewer.renderLine(match[4])
			);
		};

		let buf = ``;
		for (const day in results) {
			const dayResults = results[day];
			const plural = dayResults.length !== 1 ? "es" : "";
			buf += `<details><summary>${dayResults.length} match${plural} on `;
			buf += `<a href="view-chatlog-${roomid}--${day}">${day}</a></summary><br /><hr />`;
			buf += `<p>${dayResults.filter(Boolean).map(result => renderResult(result)).join(`<hr />`)}</p>`;
			buf += `</details><hr />`;
		}
		return buf;
	}

	async fsSearchMonth(opts) {
		let {limit, room: roomid, date: month, search} = opts;
		if (!limit || limit > MAX_RESULTS) limit = MAX_RESULTS;
		const log = await exports.LogReader.get(roomid);
		if (!log) return {results: {}, total: 0};
		const days = await log.listDays(month);
		const results = {};
		let total = 0;

		for (const day of days) {
			const dayResults = await this.fsSearchDay(roomid, day, search, limit ? limit - total : null);
			if (!dayResults.length) continue;
			total += dayResults.length;
			results[day] = dayResults;
			if (total > limit) break;
		}
		return {results, total};
	}

	/** pass a null `year` to search all-time */
	async fsSearchYear(roomid, year, search, limit) {
		if (!limit || limit > MAX_RESULTS) limit = MAX_RESULTS;
		const log = await exports.LogReader.get(roomid);
		if (!log) return {results: {}, total: 0};
		let months = await log.listMonths();
		months = months.reverse();
		const results = {};
		let total = 0;

		for (const month of months) {
			if (year && !month.includes(year)) continue;
			const monthSearch = await this.fsSearchMonth({room: roomid, date: month, search, limit});
			const {results: monthResults, total: monthTotal} = monthSearch;
			if (!monthTotal) continue;
			total += monthTotal;
			Object.assign(results, monthResults);
			if (total > limit) break;
		}
		return {results, total};
	}
	async runYearSearch(roomid, year, search, limit) {
		const {results, total} = await this.fsSearchYear(roomid, year, search, limit);
		if (!total) {
			return exports.LogViewer.error(`No matches found for ${search} on ${roomid}.`);
		}
		let buf = '';
		if (year) {
			buf += `<div class="pad"><strong><br />Searching year: ${year}: </strong><hr />`;
		}	else {
			buf += `<div class="pad"><strong><br />Searching all logs: </strong><hr />`;
		}
		buf += this.renderDayResults(results, roomid);
		if (total > limit) {
			// cap is met
			buf += `<br /><strong>Max results reached, capped at ${total > limit ? limit : MAX_RESULTS}</strong>`;
			buf += `<br /><div style="text-align:center">`;
			if (total < MAX_RESULTS) {
				buf += `<button class="button" name="send" value="/sl ${search}|${roomid}|${year}|${limit + 100}">View 100 more<br />&#x25bc;</button>`;
				buf += `<button class="button" name="send" value="/sl ${search}|${roomid}|${year}|all">View all<br />&#x25bc;</button></div>`;
			}
		}
		this.results = 0;
		return buf;
	}
	async runMonthSearch(roomid, month, search, limit, year = false) {
		const {results, total} = await this.fsSearchMonth({room: roomid, date: month, search, limit});
		if (!total) {
			return exports.LogViewer.error(`No matches found for ${search} on ${roomid}.`);
		}

		let buf = (
			`<br /><div class="pad"><strong>Searching for "${search}" in ${roomid} (${month}):</strong><hr />`
		);
		buf += this.renderDayResults(results, roomid);
		if (total > limit) {
			// cap is met & is not being used in a year read
			buf += `<br /><strong>Max results reached, capped at ${limit}</strong>`;
			buf += `<br /><div style="text-align:center">`;
			if (total < MAX_RESULTS) {
				buf += `<button class="button" name="send" value="/sl ${search},room:${roomid},date:${month},limit:${limit + 100}">View 100 more<br />&#x25bc;</button>`;
				buf += `<button class="button" name="send" value="/sl ${search},room:${roomid},date:${month},limit:3000">View all<br />&#x25bc;</button></div>`;
			}
		}
		buf += `</div>`;
		this.results = 0;
		return buf;
	}
	async getSharedBattles(userids) {
		const months = _lib.FS.call(void 0, "logs/").readdirSync().filter(f => !isNaN(new Date(f).getTime()));
		const results = [];
		for (const month of months) {
			const tiers = await _lib.FS.call(void 0, `logs/${month}`).readdir();
			for (const tier of tiers) {
				const days = await _lib.FS.call(void 0, `logs/${month}/${tier}/`).readdir();
				for (const day of days) {
					const battles = await _lib.FS.call(void 0, `logs/${month}/${tier}/${day}`).readdir();
					for (const battle of battles) {
						const content = JSON.parse(_lib.FS.call(void 0, `logs/${month}/${tier}/${day}/${battle}`).readSync());
						const players = [content.p1, content.p2].map(toID);
						if (players.every(p => userids.includes(p))) {
							const battleName = battle.slice(0, -9);
							results.push(battleName);
						}
					}
				}
			}
		}
		return results;
	}
} exports.FSLogSearcher = FSLogSearcher;

 class RipgrepLogSearcher extends Searcher {
	async ripgrepSearchMonth(opts) {
		let {raw, search, room: roomid, date: month, args} = opts;
		let results;
		let count = 0;
		if (!raw) {
			search = this.constructSearchRegex(search);
		}
		const resultSep = _optionalChain([args, 'optionalAccess', _3 => _3.includes, 'call', _4 => _4('-m')]) ? '--' : '\n';
		try {
			const options = [
				'-e', search,
				`logs/chat/${roomid}/${month}`,
				'-i',
			];
			if (args) {
				options.push(...args);
			}
			const {stdout} = await _lib.ProcessManager.exec(['rg', ...options], {
				maxBuffer: MAX_MEMORY,
				cwd: `${__dirname}/../../`,
			});
			results = stdout.split(resultSep);
		} catch (e) {
			if (e.code !== 1 && !e.message.includes('stdout maxBuffer') && !e.message.includes('No such file or directory')) {
				throw e; // 2 means an error in ripgrep
			}
			if (e.stdout) {
				results = e.stdout.split(resultSep);
			} else {
				results = [];
			}
		}
		count += results.length;
		return {results, count};
	}
	async searchLogs(
		roomid,
		search,
		limit,
		date
	) {
		if (date) {
			// if it's more than 7 chars, assume it's a month
			if (date.length > 7) date = date.substr(0, 7);
			// if it's less, assume they were trying a year
			else if (date.length < 7) date = date.substr(0, 4);
		}
		const months = (date && toID(date) !== 'all' ? [date] : await new LogReaderRoom(roomid).listMonths()).reverse();
		let count = 0;
		let results = [];
		if (!limit || limit > MAX_RESULTS) limit = MAX_RESULTS;
		if (!date) date = 'all';
		const originalSearch = search;
		const userRegex = /user-(.[a-zA-Z0-9]*)/gi;
		const user = _optionalChain([userRegex, 'access', _5 => _5.exec, 'call', _6 => _6(search), 'optionalAccess', _7 => _7[0], 'optionalAccess', _8 => _8.slice, 'call', _9 => _9(5)]);
		const userSearch = user ? `the user '${user}'` : null;
		if (userSearch) {
			const id = toID(user);
			const rest = search.replace(userRegex, '')
				.split('-')
				.filter(Boolean)
				.map(str => `.*${_lib.Utils.escapeRegex(str)}`)
				.join('');
			search = `\\|c\\|${this.constructUserRegex(id)}\\|${rest}`;
		}
		while (count < MAX_RESULTS) {
			const month = months.shift();
			if (!month) break;
			const output = await this.ripgrepSearchMonth({
				room: roomid, search, date: month,
				limit, args: [`-m`, `${limit}`, '-C', '3', '--engine=auto'], raw: !!userSearch,
			});
			results = results.concat(output.results);
			count += output.count;
		}
		if (count > MAX_RESULTS) {
			const diff = count - MAX_RESULTS;
			results = results.slice(0, -diff);
		}
		return this.renderSearchResults(results, roomid, search, limit, date, originalSearch);
	}

	renderSearchResults(
		results, roomid, search, limit,
		month, originalSearch
	) {
		results = results.filter(Boolean);
		if (results.length < 1) return exports.LogViewer.error('No results found.');
		let exactMatches = 0;
		let curDate = '';
		if (limit > MAX_RESULTS) limit = MAX_RESULTS;
		const useOriginal = originalSearch && originalSearch !== search;
		const searchRegex = new RegExp(useOriginal ? search : this.constructSearchRegex(search), "i");
		const sorted = _lib.Utils.sortBy(results, line => (
			{reverse: line.split('.txt')[0].split('/').pop()}
		)).map(chunk => chunk.split('\n').map(rawLine => {
			if (exactMatches > limit || !toID(rawLine)) return null; // return early so we don't keep sorting
			const sep = rawLine.includes('.txt-') ? '.txt-' : '.txt:';
			const [name, text] = rawLine.split(sep);
			let line = exports.LogViewer.renderLine(text, 'all');
			if (!line || name.includes('today')) return null;
				 // gets rid of some edge cases / duplicates
			let date = name.replace(`logs/chat/${roomid}${toID(month) === 'all' ? '' : `/${month}`}`, '').slice(9);
			if (searchRegex.test(rawLine)) {
				if (++exactMatches > limit) return null;
				line = `<div class="chat chatmessage highlighted">${line}</div>`;
			}
			if (curDate !== date) {
				curDate = date;
				date = `</div></details><details open><summary>[<a href="view-chatlog-${roomid}--${date}">${date}</a>]</summary>`;
			} else {
				date = '';
			}
			return `${date} ${line}`;
		}).filter(Boolean).join(' ')).filter(Boolean);
		let buf = `<div class ="pad"><strong>Results on ${roomid} for ${originalSearch ? originalSearch : search}:</strong>`;
		buf += limit ? ` ${exactMatches} (capped at ${limit})` : '';
		buf += `<hr /></div><blockquote>`;
		buf += sorted.join('<hr />');
		if (limit) {
			buf += `</details></blockquote><div class="pad"><hr /><strong>Capped at ${limit}.</strong><br />`;
			buf += `<button class="button" name="send" value="/sl ${originalSearch},room:${roomid},limit:${limit + 200}">`;
			buf += `View 200 more<br />&#x25bc;</button>`;
			buf += `<button class="button" name="send" value="/sl ${originalSearch},room:${roomid},limit:3000">`;
			buf += `View all<br />&#x25bc;</button></div>`;
		}
		return buf;
	}
	async searchLinecounts(room, month, user) {
		// don't need to check if logs exist since ripgrepSearchMonth does that
		// eslint-disable-next-line no-useless-escape
		const regexString = user ? `\\|c\\|${this.constructUserRegex(user)}\\|` : `\\|c\\|`;
		const args = user ? ['--count'] : [];
		const {results: rawResults} = await this.ripgrepSearchMonth({
			search: regexString, raw: true, date: month, room, args,
		});
		const results = {};
		for (const fullLine of rawResults) {
			const [data, line] = fullLine.split('.txt:');
			const date = data.split('/').pop();
			if (!results[date]) results[date] = {};
			if (!toID(date)) continue;
			if (user) {
				if (!results[date][user]) results[date][user] = 0;
				const parsed = parseInt(line);
				results[date][user] += isNaN(parsed) ? 0 : parsed;
			} else {
				const parts = _optionalChain([line, 'optionalAccess', _10 => _10.split, 'call', _11 => _11('|'), 'access', _12 => _12.map, 'call', _13 => _13(toID)]);
				if (!parts || parts[1] !== 'c') continue;
				const id = parts[2];
				if (!id) continue;
				if (!results[date][id]) results[date][id] = 0;
				results[date][id]++;
			}
		}
		return this.renderLinecountResults(results, room, month, user);
	}
	async getSharedBattles(userids) {
		const regexString = userids.map(id => `(?=.*?("p(1|2)":"${[...id].join('[^a-zA-Z0-9]*')}[^a-zA-Z0-9]*"))`).join('');
		const results = [];
		try {
			const {stdout} = await _lib.ProcessManager.exec(['rg', '-e', regexString, '-i', '-tjson', 'logs/', '-P']);
			for (const line of stdout.split('\n')) {
				const [name] = line.split(':');
				const battleName = name.split('/').pop();
				results.push(battleName.slice(0, -9));
			}
		} catch (e) {
			if (e.code !== 1) throw e;
		}
		return results.filter(Boolean);
	}
} exports.RipgrepLogSearcher = RipgrepLogSearcher;

 const LogSearcher = new (_configloader.Config.chatlogreader === 'ripgrep' ? RipgrepLogSearcher : FSLogSearcher)(); exports.LogSearcher = LogSearcher;

 const PM = new _lib.ProcessManager.QueryProcessManager(module, async data => {
	const start = Date.now();
	try {
		let result;
		const {date, search, roomid, limit, queryType} = data;
		switch (queryType) {
		case 'linecount':
			result = await exports.LogSearcher.searchLinecounts(roomid, date, search);
			break;
		case 'search':
			result = await exports.LogSearcher.searchLogs(roomid, search, limit, date);
			break;
		case 'sharedsearch':
			result = await exports.LogSearcher.getSharedBattles(search);
			break;
		case 'battlesearch':
			result = await exports.LogReader.findBattleLog(roomid, search);
			break;
		default:
			return exports.LogViewer.error(`Config.chatlogreader is not configured.`);
		}
		const elapsedTime = Date.now() - start;
		if (elapsedTime > 3000) {
			Monitor.slow(`[Slow chatlog query]: ${elapsedTime}ms: ${JSON.stringify(data)}`);
		}
		return result;
	} catch (e) {
		if (_optionalChain([e, 'access', _14 => _14.name, 'optionalAccess', _15 => _15.endsWith, 'call', _16 => _16('ErrorMessage')])) {
			return exports.LogViewer.error(e.message);
		}
		Monitor.crashlog(e, 'A chatlog search query', data);
		return exports.LogViewer.error(`Sorry! Your chatlog search crashed. We've been notified and will fix this.`);
	}
}, CHATLOG_PM_TIMEOUT, message => {
	if (message.startsWith(`SLOW\n`)) {
		Monitor.slow(message.slice(5));
	}
}); exports.PM = PM;

if (!exports.PM.isParentProcess) {
	// This is a child process!
	global.Config = _configloader.Config;
	global.Monitor = {
		crashlog(error, source = 'A chatlog search process', details = null) {
			const repr = JSON.stringify([error.name, error.message, source, details]);
			process.send(`THROW\n@!!@${repr}\n${error.stack}`);
		},
		slow(text) {
			process.send(`CALLBACK\nSLOW\n${text}`);
		},
	};
	global.Dex = _dex.Dex;
	global.toID = _dex.Dex.toID;
	global.Chat = _chat.Chat;
	process.on('uncaughtException', err => {
		if (_configloader.Config.crashguard) {
			Monitor.crashlog(err, 'A chatlog search child process');
		}
	});
	// eslint-disable-next-line no-eval
	_lib.Repl.start('chatlog', cmd => eval(cmd));
} else {
	exports.PM.spawn(MAX_PROCESSES);
}

const accessLog = _lib.FS.call(void 0, `logs/chatlog-access.txt`).createAppendStream();

 const pages = {
	async chatlog(args, user, connection) {
		if (!user.named) return Rooms.RETRY_AFTER_LOGIN;
		let [roomid, date, opts] = _lib.Utils.splitFirst(args.join('-'), '--', 2) 
;
		if (date) date = date.trim();
		if (!roomid || roomid.startsWith('-')) {
			this.title = '[Logs]';
			return exports.LogViewer.list(user, _optionalChain([roomid, 'optionalAccess', _17 => _17.slice, 'call', _18 => _18(1)]));
		}

		// permission check
		const room = Rooms.get(roomid);
		if (!user.trusted) {
			if (room) {
				this.checkCan('declare', null, room);
			} else {
				return this.errorReply(`Access denied.`);
			}
		}

		if (!user.can('rangeban')) {
			// Some chatlogs can only be viewed by upper staff
			if (roomid.startsWith('spl') && roomid !== 'splatoon') {
				return this.errorReply("SPL team discussions are super secret.");
			}
			if (roomid.startsWith('wcop')) {
				return this.errorReply("WCOP team discussions are super secret.");
			}
			if (UPPER_STAFF_ROOMS.includes(roomid) && !user.inRooms.has(roomid)) {
				return this.errorReply("Upper staff rooms are super secret.");
			}
		}
		if (room) {
			if (!user.can('lock') || room.settings.isPrivate === 'hidden' && !room.checkModjoin(user)) {
				if (!room.persist) return this.errorReply(`Access denied.`);
				this.checkCan('mute', null, room);
			}
		} else {
			this.checkCan('lock');
		}

		void accessLog.writeLine(`${user.id}: <${roomid}> ${date}`);
		this.title = '[Logs] ' + roomid;
		/** null = no limit */
		let limit = null;
		let search;
		if (_optionalChain([opts, 'optionalAccess', _19 => _19.startsWith, 'call', _20 => _20('search-')])) {
			let [input, limitString] = opts.split('--limit-');
			input = input.slice(7);
			search = _lib.Dashycode.decode(input);
			if (search.length < 3) return this.errorReply(`That's too short of a search query.`);
			if (limitString) {
				limit = parseInt(limitString) || null;
			} else {
				limit = 500;
			}
			opts = '';
		}
		const isAll = (toID(date) === 'all' || toID(date) === 'alltime');

		const parsedDate = new Date(date );
		const validDateStrings = ['all', 'alltime'];
		const validNonDateTerm = search ? validDateStrings.includes(date) : date === 'today';
		// this is apparently the best way to tell if a date is invalid
		if (date && isNaN(parsedDate.getTime()) && !validNonDateTerm) {
			return this.errorReply(`Invalid date.`);
		}

		if (date && search) {
			return exports.LogSearcher.runSearch(this, search, roomid, isAll ? null : date, limit);
		} else if (date) {
			if (date === 'today') {
				return exports.LogViewer.day(roomid, exports.LogReader.today(), opts);
			} else if (date.split('-').length === 3) {
				return exports.LogViewer.day(roomid, parsedDate.toISOString().slice(0, 10), opts);
			} else {
				return exports.LogViewer.month(roomid, parsedDate.toISOString().slice(0, 7));
			}
		} else {
			return exports.LogViewer.room(roomid);
		}
	},
	roomstats(args, user) {
		const room = this.extractRoom();
		if (room) {
			this.checkCan('mute', null, room);
		} else {
			if (!user.can('bypassall')) {
				return this.errorReply(`You cannot view logs for rooms that no longer exist.`);
			}
		}
		const [, date, target] = _lib.Utils.splitFirst(args.join('-'), '--', 3).map(item => item.trim());
		if (isNaN(new Date(date).getTime())) {
			return this.errorReply(`Invalid date.`);
		}
		if (!/[0-9]{4}-[0-9]{2}/.test(date)) {
			return this.errorReply(`You must specify a full date - both a year and a month.`);
		}
		this.title = `[Log Stats] ${date}`;
		return exports.LogSearcher.runLinecountSearch(this, room ? room.roomid : args[2] , date, toID(target));
	},
	battlelog(args, user) {
		const [tierName, battleNum] = args;
		const tier = toID(tierName);
		const num = parseInt(battleNum);
		if (isNaN(num)) return this.errorReply(`Invalid battle number.`);
		void accessLog.writeLine(`${user.id}: battle-${tier}-${num}`);
		return exports.LogViewer.battle(tier, num, this);
	},
	async logsaccess(query) {
		this.checkCan('rangeban');
		const type = toID(query.shift());
		if (type && !['chat', 'battle', 'all', 'battles'].includes(type)) {
			return this.errorReply(`Invalid log type.`);
		}
		let title = '';
		switch (type) {
		case 'battle': case 'battles':
			title = 'Battlelog access log';
			break;
		case 'chat':
			title = 'Chatlog access log';
			break;
		default:
			title = 'Logs access log';
			break;
		}
		const userid = toID(query.shift());
		let buf = `<div class="pad"><h2>${title}`;
		if (userid) buf += ` for ${userid}`;
		buf += `</h2><hr /><ol>`;
		const accessStream = _lib.FS.call(void 0, `logs/chatlog-access.txt`).createReadStream();
		for await (const line of accessStream.byLine()) {
			const [id, rest] = _lib.Utils.splitFirst(line, ': ');
			if (userid && id !== userid) continue;
			if (type === 'battle' && !line.includes('battle-')) continue;
			if (userid) {
				buf += `<li>${rest}</li>`;
			} else {
				buf += `<li><username>${id}</username>: ${rest}</li>`;
			}
		}
		buf += `</ol>`;
		return buf;
	},
}; exports.pages = pages;

 const commands = {
	chatlogs: 'chatlog',
	chatlog(target, room, user) {
		const [tarRoom, ...opts] = target.split(',');
		const targetRoom = tarRoom ? Rooms.search(tarRoom) : room;
		const roomid = targetRoom ? targetRoom.roomid : target;
		return this.parse(`/join view-chatlog-${roomid}--today${opts ? `--${opts.join('--')}` : ''}`);
	},

	chatloghelp() {
		const strings = [
			`/chatlog [optional room], [opts] - View chatlogs from the given room. `,
			`If none is specified, shows logs from the room you're in. Requires: % @ * # &`,
			`Supported options:`,
			`<code>txt</code> - Do not render logs.`,
			`<code>txt-onlychat</code> - Show only chat lines, untransformed.`,
			`<code>onlychat</code> - Show only chat lines.`,
			`<code>all</code> - Show all lines, including userstats and join/leave messages.`,
		];
		this.runBroadcast();
		return this.sendReplyBox(strings.join('<br />'));
	},

	sl: 'searchlogs',
	logsearch: 'searchlogs',
	searchlog: 'searchlogs',
	searchlogs(target, room) {
		target = target.trim();
		const args = target.split(',').map(item => item.trim());
		if (!target) return this.parse('/help searchlogs');
		let date = 'all';
		const searches = [];
		let limit = '500';
		let targetRoom = _optionalChain([room, 'optionalAccess', _21 => _21.roomid]);
		for (const arg of args) {
			if (arg.startsWith('room:')) {
				const id = arg.slice(5).trim().toLowerCase() ;
				if (!_lib.FS.call(void 0, `logs/chat/${id}`).existsSync()) {
					return this.errorReply(`Room "${id}" not found.`);
				}
				targetRoom = id;
			} else if (arg.startsWith('limit:')) {
				limit = arg.slice(6);
			} else if (arg.startsWith('date:')) {
				date = arg.slice(5);
			} else if (arg.startsWith('user:')) {
				args.push(`user-${toID(arg.slice(5))}`);
			} else {
				searches.push(arg);
			}
		}
		if (!targetRoom) {
			return this.parse(`/help searchlogs`);
		}
		return this.parse(
			`/join view-chatlog-${targetRoom}--${date}--search-` +
			`${_lib.Dashycode.encode(searches.join('+'))}--limit-${limit}`
		);
	},
	searchlogshelp() {
		const buffer = `<details class="readmore"><summary><code>/searchlogs [arguments]</code>: ` +
			`searches logs in the current room using the <code>[arguments]</code>.</summary>` +
			`A room can be specified using the argument <code>room: [roomid]</code>. Defaults to the room it is used in.<br />` +
			`A limit can be specified using the argument <code>limit: [number less than or equal to 3000]</code>. Defaults to 500.<br />` +
			`A date can be specified in ISO (YYYY-MM-DD) format using the argument <code>date: [month]</code> (for example, <code>date: 2020-05</code>). Defaults to searching all logs.<br />` +
			`If you provide a user argument in the form <code>user:username</code>, it will search for messages (that match the other arguments) only from that user` +
			`All other arguments will be considered part of the search ` +
			`(if more than one argument is specified, it searches for lines containing all terms).<br />` +
			"Requires: % @ # &</div>";
		return this.sendReplyBox(buffer);
	},
	topusers: 'linecount',
	roomstats: 'linecount',
	linecount(target, room, user) {
		let [roomid, month, userid] = target.split(',').map(item => item.trim());
		const tarRoom = roomid ? Rooms.search(roomid) : room;
		if (!tarRoom) return this.errorReply(`You must specify a valid room.`);
		if (!month) month = exports.LogReader.getMonth();
		return this.parse(`/join view-roomstats-${tarRoom.roomid}--${month}--${toID(userid)}`);
	},
	linecounthelp: [
		`/topusers OR /linecount [room], [month], [userid] - View room stats in the given [room].`,
		`If a user is provided, searches only for that user, else the top 100 users are shown.`,
		`Requires: % @ # &`,
	],
	slb: 'sharedloggedbattles',
	async sharedloggedbattles(target, room, user) {
		this.checkCan('lock');
		if (_configloader.Config.nobattlesearch) return this.errorReply(`/${this.cmd} has been temporarily disabled due to load issues.`);
		const targets = target.split(',').map(toID).filter(Boolean);
		if (targets.length < 2 || targets.length > 2) {
			return this.errorReply(`Specify two users.`);
		}
		const results = await exports.LogSearcher.sharedBattles(targets);
		if (_optionalChain([room, 'optionalAccess', _22 => _22.settings, 'access', _23 => _23.staffRoom]) || _optionalChain([this, 'access', _24 => _24.pmTarget, 'optionalAccess', _25 => _25.isStaff])) {
			this.runBroadcast();
		}
		return this.sendReplyBox(results);
	},
	sharedloggedbattleshelp: [
		`/sharedloggedbattles OR /slb [user1, user2] - View shared battle logs between user1 and user2`,
	],
	battlelog(target, room, user) {
		this.checkCan('lock');
		target = target.trim();
		if (!target) return this.errorReply(`Specify a battle.`);
		if (target.startsWith('http://')) target = target.slice(7);
		if (target.startsWith('https://')) target = target.slice(8);
		if (target.startsWith(`${_configloader.Config.routes.client}/`)) target = target.slice(_configloader.Config.routes.client.length + 1);
		if (target.startsWith(`${_configloader.Config.routes.replays}/`)) target = `battle-${target.slice(_configloader.Config.routes.replays.length + 1)}`;
		if (target.startsWith('psim.us/')) target = target.slice(8);
		return this.parse(`/join view-battlelog-${target}`);
	},
	logsaccess(target, room, user) {
		this.checkCan('rangeban');
		const [type, userid] = target.split(',').map(toID);
		return this.parse(`/j view-logsaccess-${type || 'all'}${userid ? `-${userid}` : ''}`);
	},
	gcsearch: 'groupchatsearch',
	async groupchatsearch(target, room, user) {
		this.checkCan('lock');
		target = target.toLowerCase().replace(/[^a-z0-9-]+/g, '');
		if (!target) return this.parse(`/help groupchatsearch`);
		if (target.length < 3) {
			return this.errorReply(`Too short of a search term.`);
		}
		const files = await _lib.FS.call(void 0, `logs/chat`).readdir();
		const buffer = [];
		for (const roomid of files) {
			if (roomid.startsWith('groupchat-') && roomid.includes(target)) {
				buffer.push(roomid);
			}
		}
		_lib.Utils.sortBy(buffer, roomid => !!Rooms.get(roomid));
		return this.sendReplyBox(
			`Groupchats with a roomid matching '${target}': ` +
			(buffer.length ? buffer.map(id => `<a href="/view-chatlog-${id}">${id}</a>`).join('; ') : 'None found.')
		);
	},
	groupchatsearchhelp: [
		`/groupchatsearch [target] - Searches for logs of groupchats with names containing the [target]. Requires: % @ &`,
	],
}; exports.commands = commands;

 //# sourceMappingURL=sourceMaps/chatlog.js.map