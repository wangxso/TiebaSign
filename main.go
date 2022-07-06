package main

import (
	"crypto/md5"
	"fmt"
	"io/ioutil"
	"math/rand"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/eddieivan01/nic"
	"github.com/sirupsen/logrus"
	"github.com/wangxso/TiebaSign/bizconst"
	"gopkg.in/yaml.v2"
)

type Config struct {
	BDUSS string `yaml:"BDUSS"`
}

type TBS struct {
	Tbs     string `json:"tbs"`
	IsLogin int    `json:"is_login"`
}

var config Config
var session *nic.Session
var wg sync.WaitGroup

func init() {
	logrus.SetLevel(logrus.TraceLevel)
	session = &nic.Session{}

	yamlFile, err := ioutil.ReadFile("./config.yaml")
	if err != nil {
		logrus.Error("read file: " + err.Error())
	}
	err = yaml.Unmarshal(yamlFile, &config)
	if err != nil {
		logrus.Error("unmarshal: " + err.Error())
	}
	logrus.Info("load bduss: " + config.BDUSS)
}

func getTbs(bduss string) (tbs string) {
	logrus.Info("开始获取tbs")
	headers := make(nic.KV, 0)
	headers["Cookie"] = bizconst.BDUSS + bizconst.Equal + bduss
	headers["Host"] = "tieba.baidu.com"
	headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33"

	resp, err := session.Get(bizconst.TBSURL, nic.H{
		Headers: headers,
	})
	if err != nil {
		logrus.Error(err.Error())
	}
	var tbsJson TBS
	resp.JSON(&tbsJson)
	tbs = tbsJson.Tbs
	return
}

func MD5(str string) string {
	data := []byte(str) //切片
	has := md5.Sum(data)
	md5str := fmt.Sprintf("%x", has) //将[]byte转成16进制
	return md5str
}

func encodeData(data nic.KV) (sign string) {
	s := bizconst.EmptyStr
	keys := make([]string, 0)
	for key := range data {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	for _, key := range keys {
		s += key + bizconst.Equal + data[key].(string)
	}
	sign = MD5((s + bizconst.SignKey))
	sign = strings.ToUpper(sign)
	return
}

func getFavorite(bduss string) (t []map[string]interface{}) {
	logrus.Info("开始获取关注的贴吧")
	// 客户端关注的贴吧
	// returnData := make([]string, 1)
	data := make(nic.KV, 0)
	data["BDUSS"] = bduss
	data["_client_type"] = "2"
	data["_client_id"] = "wappc_1534235498291_488"
	data["_client_version"] = "9.7.8.0"
	data["_phone_imei"] = "000000000000000"
	data["from"] = "1008621y"
	data["page_no"] = "1"
	data["page_size"] = "200"
	data["model"] = "MI+5"
	data["net_type"] = "1"
	data["timestamp"] = strconv.FormatInt(time.Now().Unix(), 10)
	// data["timestamp"] = "1657030504"
	data["vcode_tag"] = "11"
	data[bizconst.Sign] = encodeData(data)
	i := 1
	resp, err := nic.Post(bizconst.LikieURL, nic.H{
		Data: data,
	})

	if err != nil {
		logrus.Error(err.Error())
	}

	result := make(nic.KV, 0)
	err = resp.JSON(&result)
	if err != nil {
		logrus.Error("Json err: ", err.Error())
	}

	keys := make(map[string]bool, 0)
	for k := range result {
		keys[k] = true
	}
	res := make([]map[string]interface{}, 0)
	res = append(res, result)

	for keys["has_more"] && result["has_more"].(string) == "1" {
		i += 1
		data["BDUSS"] = bduss
		data["_client_type"] = "2"
		data["_client_id"] = "wappc_1534235498291_488"
		data["_client_version"] = "9.7.8.0"
		data["_phone_imei"] = "000000000000000"
		data["from"] = "1008621y"
		data["page_no"] = strconv.Itoa(i)
		data["page_size"] = "200"
		data["model"] = "MI+5"
		data["net_type"] = "1"
		data["timestamp"] = strconv.FormatInt(time.Now().Unix(), 10)
		data["vcode_tag"] = "11"
		data[bizconst.Sign] = encodeData(data)
		resp, err := session.Post(bizconst.LikieURL, nic.H{
			Data: data,
		})

		if err != nil {
			logrus.Error(err.Error())
		}
		err = resp.JSON(&result)
		if err != nil {
			logrus.Error("Json err: ", err.Error())
		}
		keys := make(map[string]bool, 0)
		for k := range result {
			keys[k] = true
		}
		res = append(res, result)
	}

	for _, s := range res {
		forumList := s["forum_list"].(map[string]interface{})
		GconForm := forumList["non-gconforum"].([]interface{})
		for _, m := range GconForm {
			mList, ok := m.([]interface{})
			if ok {
				for _, k := range mList {
					t = append(t, k.(map[string]interface{}))
				}
			} else {
				t = append(t, m.(map[string]interface{}))
			}
		}
	}
	return
}

func clientSign(bduss, tbs, fid, kw string, idx, count int) {
	logrus.Info("【" + kw + "】吧,开始签到(" + strconv.Itoa(idx) + "/" + strconv.Itoa(count) + ")")
	headers := make(nic.KV, 0)
	headers["Cookie"] = bizconst.BDUSS + bizconst.Equal + bduss
	headers["Host"] = "tieba.baidu.com"
	headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33"
	data := make(nic.KV, 0)
	data["BDUSS"] = bduss
	data["_client_type"] = "2"
	data["_client_version"] = "9.7.8.0"
	data["_phone_imei"] = "000000000000000"
	data["model"] = "MI+5"
	data["net_type"] = "1"
	data["timestamp"] = strconv.FormatInt(time.Now().Unix(), 10)
	// data["timestamp"] = "1657030504"
	data["vcode_tag"] = "11"
	data[bizconst.Fid] = fid
	data[bizconst.KW] = kw
	data["tbs"] = tbs
	data[bizconst.Sign] = encodeData(data)

	resp, err := session.Post(bizconst.SignURL, nic.H{
		Data:    data,
		Headers: headers,
	})
	if err != nil {
		logrus.Error("[ClientSign] post error: ", err.Error())
	}
	res := make(map[string]interface{}, 0)
	resp.JSON(&res)
	if res["error_code"] == "0" {
		userInfo := res["user_info"].(map[string]interface{})
		logrus.Info("签到成功, 你是第", userInfo["user_sign_rank"], "个签到的")
	} else {
		logrus.Error("签到失败, 错误信息: ", res["error_msg"])
	}
	wg.Done()
}

func main() {
	rand.New(rand.NewSource(time.Now().UnixNano()))
	if config.BDUSS == "" {
		logrus.Info("No BDUSS load, 请检查配置文件")
		return
	}
	logrus.Info("用户开始签到")
	tbs := getTbs(config.BDUSS)
	logrus.Info("获取TBS成功")
	t := getFavorite(config.BDUSS)
	count := len(t)
	logrus.Info("一共", count, "个吧，开始签到")
	start := time.Now()
	for idx, j := range t {
		wg.Add(1)
		time.Sleep(time.Second * (time.Duration(rand.Int31()) % 2))
		go clientSign(config.BDUSS, tbs, j["id"].(string), j["name"].(string), idx, count)
	}
	wg.Wait()
	logrus.Info("签到耗时: ", time.Since(start))
}
